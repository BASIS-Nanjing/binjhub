import json
import sqlite3

import identity
import identity.web
from flask import (
    Flask,
    make_response,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.middleware.proxy_fix import ProxyFix

import app_config
from database import RF_ALL, RF_PENDING, UF_ADMIN, Database
from flask_session import Session

app = Flask(__name__, static_url_path='/')
app.config.from_object(app_config)
if app_config.SESSION_SQLALCHEMY is not None:
    app_config.SESSION_SQLALCHEMY.init_app(app)
    connect = lambda: app_config.SESSION_SQLALCHEMY.engine.raw_connection()
else:
    connect = lambda: sqlite3.connect('data.db')
Session(app)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

auth = identity.web.Auth(
    session=session,
    authority=app.config['AUTHORITY'],
    client_id=app.config['CLIENT_ID'],
    client_credential=app.config['CLIENT_SECRET'],
)

with app.app_context():
    database = Database(connect)


def _user():
    user = auth.get_user()
    if user is not None:
        return database.get_user_by_email(user['email'])


def _dump_user(user=None):
    if user is None:
        user = _user()
        assert user, 'User is not logged in'
    return {'name': user.name, 'email': user.email, 'flag': user.flag}


def _json(message, code=200):
    resp = make_response(json.dumps({'success': code < 400, 'message': message}), code)
    resp.content_type = 'application/json'
    return resp


def _unauthorized():
    return _json('User is not logged in', 401)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/api/auth')
def auth_root():
    if request.args.get('returnUrl'):
        session['return_url'] = request.args.get('returnUrl')
    return redirect(
        auth.log_in(
            scopes=app.config['SCOPE'],
            redirect_uri=url_for('auth_callback', _external=True),
        )['auth_uri']
    )


@app.route('/api/auth/callback')
def auth_callback():
    res = auth.complete_log_in(request.args)
    assert res
    if 'error' in res:
        msg = 'Auth error %s' % res['error']
        if 'error_description' in res:
            msg += ': %s' % res['error_description']
        session['auth_error'] = msg
    user = _user()
    if user is None and 'error' not in res:
        database.add_user(res['email'], res['name'])
    if session.get('return_url'):
        url = session.pop('return_url')
        return redirect(url)
    return redirect(url_for('home'))


@app.route('/api/auth/logout')
def auth_logout():
    url = request.args.get('returnUrl') or url_for('home', _external=True)
    logout = request.args.get('upstream', '1')
    logout = logout not in ['false', '0']
    res = auth.log_out(url)
    if logout:
        return redirect(res)
    return redirect(url)


@app.route('/api/me')
def me():
    if 'auth_error' in session:
        return _json(session.pop('auth_error'), 500)
    user = _user()
    if user is None:
        return _unauthorized()
    data = {'success': True, 'message': '', 'data': _dump_user(user)}
    return json.dumps(data)


@app.route('/api/recommendations')
def api_get_recommendations():
    try:
        skip = int(request.args.get('skip', 0))
        top = int(request.args.get('top', -1))
        order_by = request.args.get('orderBy', 'modified')
        assert order_by in ['modified', 'created', 'id']
    except:
        return _json('Invalid parameters', 400)
    flag = 0
    user = _user()
    uid = None
    if user is not None:
        uid = user.email
        uf = user.flag
        flag = RF_ALL if uf & UF_ADMIN else 0
    results = database.list_recommendations(
        skip=skip, top=top, order_by=order_by, flag=flag, extra_email=uid
    )
    data = []
    for res in results:
        up, down = database.get_vote_counts_by_recommendation(res.id)
        if user is not None:
            uv = database.get_user_vote(uid, res.id)
            uup, udown = (uv.up, uv.down) if uv is not None else (0, 0)
        else:
            uup, udown = 0, 0
        data.append(
            {
                'id': res.id,
                'title': res.title,
                'url': res.url,
                'reason': res.reason,
                'flag': res.flag,
                'votes': {'up': up, 'down': down},
                'myVotes': {'up': int(uup), 'down': int(udown)},
                'user': _dump_user(user),
            }
        )
    ret = {'success': True, 'message': '', 'data': data}
    return json.dumps(ret)


if app_config.SESSION_SQLALCHEMY is not None:
    with app.app_context():
        app_config.SESSION_SQLALCHEMY.create_all()

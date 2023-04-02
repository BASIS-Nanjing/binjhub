import json

import identity
import identity.web
from flask import (
    Flask,
    make_response,
    redirect,
    request,
    render_template,
    session,
    url_for,
)
from werkzeug.middleware.proxy_fix import ProxyFix

import app_config
from flask_session import Session

app = Flask(__name__, static_url_path='/')
app.config.from_object(app_config)
if app_config.SESSION_SQLALCHEMY is not None:
    app_config.SESSION_SQLALCHEMY.init_app(app)
Session(app)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

auth = identity.web.Auth(
    session=session,
    authority=app.config['AUTHORITY'],
    client_id=app.config['CLIENT_ID'],
    client_credential=app.config['CLIENT_SECRET'],
)


def _unauthorized():
    return make_response(
        json.dumps({'success': False, 'message': 'User is not logged in'}), 401
    )


@app.route('/')
def home():
    return render_template('index.html', user=auth.get_user())


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
        session['auth_error'] = res
    if 'return_url' in session and session['return_url']:
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
    user = auth.get_user()
    if user is None:
        return _unauthorized()
    if 'name' not in user:
        return make_response(
            json.dumps({'success': False, 'message': 'User name not found'}), 401
        )
    if 'email' not in user:
        return make_response(
            json.dumps({'success': False, 'message': 'User email not found'}), 401
        )
    data = {
        'success': True,
        'message': '',
        'data': {'name': user['name'], 'email': user['email']},
    }
    return json.dumps(data)


if app_config.SESSION_SQLALCHEMY is not None:
    with app.app_context():
        app_config.SESSION_SQLALCHEMY.create_all()

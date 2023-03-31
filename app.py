import json

import identity
import identity.web
from flask import Flask, redirect, request, send_file, session, url_for
from werkzeug.middleware.proxy_fix import ProxyFix
import app_config
from flask_session import Session

app = Flask(__name__, static_url_path='/')
app.config.from_object(app_config)
app_config.SESSION_SQLALCHEMY.init_app(app)
Session(app)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

auth = identity.web.Auth(
    session=session,
    authority=app.config['AUTHORITY'],
    client_id=app.config['CLIENT_ID'],
    client_credential=app.config['CLIENT_SECRET'],
)


@app.route('/')
def home():
    return send_file('static/index.html')


@app.route('/api/auth')
def auth_root():
    return redirect(
        auth.log_in(
            scopes=app.config['SCOPE'],
            redirect_uri=url_for('auth_callback', _external=True),
        )['auth_uri']
    )


@app.route('/api/auth/status')
def auth_status():
    return json.dumps(auth.get_user())


@app.route('/api/auth/callback')
def auth_callback():
    res = auth.complete_log_in(request.args)
    return redirect('/api/auth/status')

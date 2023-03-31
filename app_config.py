import os

from flask_sqlalchemy import SQLAlchemy

CLIENT_ID = os.getenv('BINJHUB_CLIENT_ID')
CLIENT_SECRET = os.getenv('BINJHUB_CLIENT_SECRET')
AUTHORITY = 'https://login.microsoftonline.com/%s' % os.getenv('BINJHUB_TENANT_ID', 'common')
SESSION_TYPE = 'filesystem'
SCOPE = []

if os.getenv('POSTGRESQL'):
    SESSION_TYPE = 'sqlalchemy'
    SQLALCHEMY_DATABASE_URI = os.getenv('POSTGRESQL')
    SESSION_SQLALCHEMY = SQLAlchemy()
    SESSION_SQLALCHEMY_TABLE = 'sessions'

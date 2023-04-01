import os

API_VERSION = '1.1.0'

CLIENT_ID = os.getenv('BINJHUB_CLIENT_ID')
CLIENT_SECRET = os.getenv('BINJHUB_CLIENT_SECRET')
AUTHORITY = 'https://login.microsoftonline.com/%s' % os.getenv(
    'BINJHUB_TENANT_ID', 'common'
)
SESSION_TYPE = 'filesystem'
SCOPE = ['email']

SESSION_SQLALCHEMY = None

if os.getenv('POSTGRESQL'):
    from flask_sqlalchemy import SQLAlchemy

    SESSION_TYPE = 'sqlalchemy'
    SQLALCHEMY_DATABASE_URI = os.getenv('POSTGRESQL')
    SESSION_SQLALCHEMY = SQLAlchemy()
    SESSION_SQLALCHEMY_TABLE = 'sessions'

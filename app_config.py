import os

CLIENT_ID = os.getenv('BINJHUB_CLIENT_ID')
CLIENT_SECRET = os.getenv('BINJHUB_CLIENT_SECRET')
AUTHORITY = 'https://login.microsoftonline.com/%s' % os.getenv('BINJHUB_TENANT_ID', 'common')
SESSION_TYPE = 'filesystem'
SCOPE = []

if os.getenv('POSTGRESQL'):
    SESSION_TYPE = 'sqlalchemy'
    SESSION_SQLALCHEMY = os.getenv('POSTGRESQL')
    SESSION_SQLALCHEMY_TABLE = 'sessions'

import time
from threading import get_ident

__version__ = '1.0.0'

CREATE_USERS = '''CREATE TABLE IF NOT EXISTS users (
    email TEXT PRIMARY KEY,
    name TEXT,
    flag INTEGER
);'''
CREATE_REC = '''CREATE TABLE IF NOT EXISTS recommendations (
    id INTEGER PRIMARY KEY,
    email TEXT,
    title TEXT,
    url TEXT,
    reason TEXT,
    flag INTEGER,
    created INTEGER,
    modified INTEGER
);'''
CREATE_VOTES = '''CREATE TABLE IF NOT EXISTS votes (
    id INTEGER PRIMARY KEY,
    recid INTEGER,
    email TEXT,
    up INTEGER,
    down INTEGER
);'''


class Database:
    def __init__(self, connect) -> None:
        self._connect = connect
        self._cache = {}
        db = self._database
        cur = db.cursor()
        cur.execute(CREATE_USERS)
        cur.execute(CREATE_REC)
        cur.execute(CREATE_VOTES)
        db.commit()

    @property
    def _database(self):
        ident = get_ident()
        if ident in self._cache:
            return self._cache[ident]
        self._cache[ident] = connection = self._connect()
        return connection

    def _execute(self, sql, parameters=[]):
        return self._database.cursor().execute(sql, parameters)

    def get_recommendations_by_user(self, email, skip=0, top=-1, order_by='modified'):
        if order_by not in ['modified', 'created', 'id']:
            raise ValueError('Cannot sort by %r' % order_by)
        sql = (
            'SELECT * FROM recommendations WHERE email=?'
            ' ORDER BY %s DESC LIMIT %d OFFSET %d' % (order_by, top, skip)
        )
        res = self._execute(sql, [email]).fetchall()
        return [Recommendation(*x) for x in res]

    def get_votes_by_recommendation(self, recommendation_id, skip=0, top=-1):
        sql = 'SELECT * FROM votes WHERE recid=? LIMIT %d OFFSET %d' % (top, skip)
        res = self._execute(sql, [recommendation_id]).fetchall()
        return [Vote(*x) for x in res]

    def get_vote_counts_by_recommendation(self, recommendation_id):
        sql = 'SELECT COUNT() FROM votes WHERE recid=? AND up=1'
        up = self._execute(sql, [recommendation_id]).fetchone()[0]
        sql = 'SELECT COUNT() FROM votes WHERE recid=? AND down=1'
        down = self._execute(sql, [recommendation_id]).fetchone()[0]
        return up, down

    def get_votes_by_user(self, email, skip=0, top=-1):
        sql = 'SELECT * FROM votes WHERE email=? LIMIT %d OFFSET %d' % (top, skip)
        res = self._execute(sql, [email]).fetchall()
        return [Vote(*x) for x in res]

    def get_user_vote(self, email, recommendation_id):
        sql = 'SELECT * FROM votes WHERE email=? AND recid=?'
        res = self._execute(sql, [email, recommendation_id]).fetchone()
        if res:
            return Vote(*res)

    def get_recommendation_by_id(self, id):
        sql = 'SELECT * FROM recommendations WHERE id=?'
        res = self._execute(sql, [id]).fetchone()
        if res:
            return Recommendation(*res)

    def get_vote_by_id(self, id):
        sql = 'SELECT * FROM votes WHERE id=?'
        res = self._execute(sql, [id]).fetchone()
        if res:
            return Vote(*res)

    def get_user_by_email(self, email):
        sql = 'SELECT * FROM users WHERE email=?'
        res = self._execute(sql, [email]).fetchone()
        if res:
            return User(*res)

    def list_recommendations(self, skip=0, top=-1, order_by='modified'):
        if order_by not in ['modified', 'created', 'id']:
            raise ValueError('Cannot sort by %r' % order_by)
        sql = 'SELECT * FROM recommendations ORDER BY %s DESC LIMIT %d OFFSET %d' % (
            order_by,
            top,
            skip,
        )
        res = self._execute(sql).fetchall()
        return [Recommendation(*x) for x in res]

    def add_user(self, email, name):
        sql = 'INSERT INTO users(email, name) VALUES(?, ?)'
        db = self._database
        cur = db.cursor()
        try:
            cur.execute(sql, [email, name])
        except:
            return False
        db.commit()
        return True

    def add_recommendation(self, email, title, url, reason):
        sql = (
            'INSERT INTO recommendations(email, title, url, reason, modified, created)'
            ' VALUES(?, ?, ?, ?, ?, ?)'
        )
        ctime = int(time.time() * 1000)
        db = self._database
        cur = db.cursor()
        cur.execute(sql, [email, title, url, reason, ctime, ctime])
        db.commit()

    def update_vote(self, email, recommendation_id, up, down):
        if self.get_user_vote(email, recommendation_id) is None:
            sql = 'INSERT INTO votes(recid, email, up, down) VALUES(?, ?, ?, ?)'
            params = [recommendation_id, email, up, down]
        else:
            sql = 'UPDATE votes SET up=?, down=? WHERE recid=? AND email=?'
            params = [up, down, recommendation_id, email]
        db = self._database
        cur = db.cursor()
        cur.execute(sql, params)
        db.commit()

    def patch_recommendation(self, id, *, reason):
        sql = 'UPDATE recommendations SET reason=? WHERE id=?'
        db = self._database
        cur = db.cursor()
        try:
            cur.execute(sql, [reason, id])
        except:
            return False
        db.commit()
        return True
    
    def delete_recommendation(self, id):
        sql = 'DELETE FROM recommendations WHERE id=?'
        db = self._database
        cur = db.cursor()
        try:
            cur.execute(sql, [id])
        except:
            return False
        db.commit()
        return True

    def delete_vote(self, id):
        sql = 'DELETE FROM votes WHERE id=?'
        db = self._database
        cur = db.cursor()
        try:
            cur.execute(sql, [id])
        except:
            return False
        db.commit()
        return True


class Recommendation:
    __slots__ = 'id', 'email', 'title', 'url', 'reason', 'created', 'modified'

    def __init__(self, id, email, title, url, reason, created, modified):
        self.id = id
        self.email = email
        self.title = title
        self.url = url
        self.reason = reason
        self.created = created
        self.modified = modified


class Vote:
    __slots__ = 'id', 'recommendation_id', 'email', 'up', 'down'

    def __init__(self, id, recommendation_id, email, up, down):
        self.id = id
        self.recommendation_id = recommendation_id
        self.email = email
        self.up = bool(up)
        self.down = bool(down)


class User:
    __slots__ = 'email', 'name'

    def __init__(self, email, name):
        self.email = email
        self.name = name

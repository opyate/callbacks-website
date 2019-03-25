from psycopg2.extensions import ISOLATION_LEVEL_READ_COMMITTED, ISOLATION_LEVEL_AUTOCOMMIT
from callbacksweb.model.callback import Callback
from callbacksweb.model.user import User
import psycopg2
from psycopg2 import sql
from typing import List


# insert into callbacks (url, ts, user_id) values ('http://example.org', 123, 'demouser')
def insert_callback(config, callback_url, ts, user_id ='demouser'):
    url = config.DATABASE_URL
    with psycopg2.connect(url) as cnn:
        cnn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        with cnn.cursor() as cur:
            cur.execute(
                sql.SQL("insert into callbacks (url, ts, user_id) values (%s, %s::integer, %s) RETURNING *").format(),
                [callback_url, ts, user_id]
            )
            return Callback(cur.fetchone())


def read_callbacks(config, user_id) -> List[Callback]:
    callbacks = []
    url = config.DATABASE_URL
    with psycopg2.connect(url) as cnn:
        cnn.set_isolation_level(ISOLATION_LEVEL_READ_COMMITTED)
        with cnn.cursor() as cur:
            cur.execute(
                sql.SQL("select * from callbacks where user_id = %s").format(),
                [user_id]
            )

            row = cur.fetchone()
            while row:
                callbacks.append(Callback(row))
                row = cur.fetchone()
    print('db found %i callbacks' % len(callbacks))
    return callbacks


def read_user(config, user_id) -> List[Callback]:
    callbacks = []
    url = config.DATABASE_URL
    with psycopg2.connect(url) as cnn:
        cnn.set_isolation_level(ISOLATION_LEVEL_READ_COMMITTED)
        with cnn.cursor() as cur:
            cur.execute(
                sql.SQL("select * from users where user_id = %s").format(),
                [user_id]
            )

            row = cur.fetchone()
            if row:
                return User(row)

def insert_user(config, user_id, api_key):
    url = config.DATABASE_URL
    with psycopg2.connect(url) as cnn:
        cnn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        with cnn.cursor() as cur:
            cur.execute(
                sql.SQL("insert into users (user_id, api_key) values (%s, %s) RETURNING *").format(),
                [user_id, api_key]
            )
            return User(cur.fetchone())
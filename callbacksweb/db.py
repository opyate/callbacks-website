from psycopg2.extensions import ISOLATION_LEVEL_READ_COMMITTED, ISOLATION_LEVEL_AUTOCOMMIT
from callbacksweb.model.callback import Callback
import psycopg2
from psycopg2 import sql
from typing import List


# insert into callbacks (url, ts, user_id) values ('http://example.org', 123, 'demouser')
def insert(config, callback_url, ts, user_id = 'demouser'):
    url = config.DATABASE_URL
    with psycopg2.connect(url) as cnn:
        cnn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        with cnn.cursor() as cur:
            cur.execute(
                sql.SQL("insert into callbacks (url, ts, user_id) values (%s, %s::integer, %s)").format(),
                [callback_url, ts, user_id]
            )

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

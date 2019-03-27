import logging
from aiohttp import web
from callbacksweb.db import insert_callback, read_callbacks, read_callback, count_callbacks, delete_callback
from callbacksweb.config import DevConfig, ProdConfig
import os
import base64
import sys, traceback
import jsonpickle
import json
import uuid
from callbacksweb.handlers.util import js
import psycopg2


config = DevConfig
if 'DO_PROD' in os.environ:
    config = ProdConfig


log = logging.getLogger(__name__)


def safe_callback(callback):
    ret = js(callback)
    ret.pop('user_id')
    ret.pop('shard')
    return ret


async def handle(request):
    # non-auth user is not allowed to do anything
    # demo user is allowed to use cbapi.uys.io/test as a url
    # anyone else can use anything else

    try:

        if request.method == 'DELETE':
            callback_id = request.match_info['id']
            count = delete_callback(config, request['uid'], callback_id)

            return web.json_response({
                'message': 'Deleted {} row(s).'.format(count)
            })

        if request.method == 'POST':
            if request.content_type == 'application/json':
                data = await request.json()
            else:
                data = await request.post()
            url = data['url']

            ts = int(data['ts'])

            # convert to seconds
            if ts > 9999999999:
                ts = ts // 1000
            callback = insert_callback(config, url, ts, request['uid'])

            return web.json_response(safe_callback(callback))

        if request.method == 'GET':
            if 'id' in request.match_info:
                callback_id = request.match_info['id']
                callback = read_callback(config, request['uid'], callback_id)

                return web.json_response(safe_callback(callback))
            else:
                limit = 100
                if 'limit' in request.query:
                    limit = int(request.query['limit'])
                offset = 0
                if 'offset' in request.query:
                    offset = int(request.query['offset'])
                callbacks = read_callbacks(config, request['uid'], limit, offset)
                count = count_callbacks(config, request['uid'])
                ret = [safe_callback(callback) for callback in callbacks]
                return_value = {
                    'results': ret,
                    'offset': offset,
                    'limit': limit,
                    'count': count,
                    "_links": {
                        "current": {
                            "href": "/callbacks?limit={}&offset={}".format(limit, offset)
                        },
                        "self": {
                            "href": "/callbacks"
                        }
                    }
                }

                if count > limit:
                    return_value['_links']['next'] = {"href": "/callbacks?limit={}&offset={}".format(limit, offset + limit)}
                if offset > 0:
                    return_value['_links']['prev'] = {"href": "/callbacks?limit={}&offset={}".format(limit, offset - limit)}

                return web.json_response(return_value)

    except KeyError:
        return web.json_response({
            'message': 'API key required'
        }, status=401)
    except psycopg2.DataError:
        return web.json_response({
            'message': 'Could not find that resource'
        }, status=404)
    except Exception as e:
        correlation_id = str(uuid.uuid4())
        print(correlation_id)
        traceback.print_exc(file=sys.stdout)
        return web.json_response({
            'message': 'Something went wrong :(',
            'correlation_id': correlation_id
        }, status=500)

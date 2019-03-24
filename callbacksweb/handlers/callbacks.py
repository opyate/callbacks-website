import logging
import aiohttp_jinja2
from aiohttp import web
from callbacksweb.db import insert, read_callbacks
from callbacksweb.config import DevConfig, ProdConfig
import os
import base64
import sys, traceback


config = DevConfig
if 'DO_PROD' in os.environ:
    config = ProdConfig


log = logging.getLogger(__name__)


async def handle(request):
    # non-auth user is not allowed to do anything
    # demo user is allowed to use cbapi.uys.io/test as a url
    # anyone else can use anything else

    try:
        apikey = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            auth_header = auth_header.replace('Basic ', '')
            apikey = base64.b64decode(auth_header).decode('utf-8').split(':')[0]

        if request.method == 'POST':
            if request.content_type == 'application/json':
                data = await request.json()
            else:
                data = await request.post()
            url = data['url']

            # demo user is only allowed to use cb.uys.io as callback target
            if 'DO_PROD' in os.environ and apikey == 'demo' and 'cb.uys.io/test' not in url:
                return web.Response(text='demo user only allowed cb.uys.io/test', status=400)

            ts = int(data['ts'])

            # convert to seconds
            if ts > 9999999999:
                ts = ts // 1000
            print('submitted', url, ts)
            # TODO real username here
            # TODO apikey should now be in users table (do that on signup)
            insert(config, url, ts, 'demouser')

        callbacks = read_callbacks(config, 'demouser')
        print('found %i callbacks' % len(callbacks))
        # [print(callback) for callback in callbacks]

        return web.Response(text='Great, now back to the site and wait for the result!')
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        return web.Response(text='Something went wrong :(', status=500)


import logging
import aiohttp
import aiohttp_jinja2
from aiohttp import web
from callbacksweb.db import insert, read_callbacks
import uuid
import random
from callbacksweb.config import DevConfig, ProdConfig
import os
import datetime
import base64
import sys, traceback


config = DevConfig
if 'DO_PROD' in os.environ:
    config = ProdConfig


log = logging.getLogger(__name__)


def getself(request):
    host = request.host
    scheme = request.scheme
    return '{}://{}'.format(scheme, host)

async def fake_endpoint(request):
    if request.method == 'POST':
        data = await request.json()
    elif request.method == 'GET':
        data = request.query

    # set up websocket client
    session = aiohttp.ClientSession()
    ws = await session.ws_connect(
        url=getself(request))

    payload = 'no payload'
    if 'payload' in data:
        payload: str = data['payload']
        if len(payload) > 30:
            payload = payload[:30] + '..'
        await ws.send_str(payload)
        await ws.close()

    return web.Response(text=payload)

async def index(request):
    ws_current = web.WebSocketResponse()
    ws_ready = ws_current.can_prepare(request)
    if not ws_ready.ok:
        return aiohttp_jinja2.render_template('index.html', request, {})

    await ws_current.prepare(request)

    name = str(uuid.uuid4())
    log.info('%s joined.', name)

    await ws_current.send_json({'action': 'connect', 'name': name})

    for ws in request.app['websockets'].values():
        await ws.send_json({'action': 'join', 'name': name})
    request.app['websockets'][name] = ws_current

    while True:
        msg = await ws_current.receive()

        if msg.type == aiohttp.WSMsgType.text:
            open_sockets = request.app['websockets'].values()
            for ws in open_sockets:
                if ws is not ws_current or len(open_sockets) == 1:
                    if msg.data == 'demo-ten' or msg.data == 'demo-thirty':
                        n = 10
                        if msg.data == 'demo-thirty':
                            n = 30

                        url = getself(request) + '/api?payload=' + name
                        n_secs_from_now = datetime.datetime.now() + datetime.timedelta(seconds=n)
                        # unix time in seconds
                        ts = int(n_secs_from_now.strftime("%s"))
                        print('inserting ' + url)
                        insert(config, url, ts, 'demouser')

                if ws is not ws_current:
                    await ws.send_json(
                        {'action': 'sent', 'name': '', 'text': msg.data})
        else:
            break

    del request.app['websockets'][name]
    log.info('%s disconnected.', name)
    for ws in request.app['websockets'].values():
        await ws.send_json({'action': 'disconnect', 'name': name})

    return ws_current


async def create_callback(request):
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

        if request.content_type == 'application/json':
            return web.Response(text='Great, now back to the site and wait for the result!')
        else:
            return aiohttp_jinja2.render_template('callbacks.html', request, {'callbacks': callbacks})
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        return web.Response(text='Something went wrong :(', status=500)


async def show_config(request):
    msg = 'config is %s' % config
    print(msg)
    return web.Response(text=msg)

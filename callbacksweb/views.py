import logging
import aiohttp
import aiohttp_jinja2
from aiohttp import web
from faker import Faker
from callbacksweb.db import insert, read_callbacks
import uuid
from callbacksweb.config import DevConfig, ProdConfig
import os
config = DevConfig
if 'DO_PROD' in os.environ:
    config = ProdConfig



log = logging.getLogger(__name__)


def get_random_name():
    fake = Faker()
    return fake.name()


async def fake_endpoint(request):
    if request.method == 'POST':
        data = await request.json()
    elif request.method == 'GET':
        data = request.query

    host = request.headers['Host']
    scheme = request.scheme
    # set up websocket client
    session = aiohttp.ClientSession()
    ws = await session.ws_connect(
        url='{}://{}'.format(scheme, host))

    payload = 'no payload'
    if 'payload' in data:
        payload = data['payload']
        # await ws.send_json({'action': 'sent', 'name': 'Joe', 'text': payload})
        await ws.send_str(payload)
        await ws.close()

    return web.Response(text=payload)

async def index(request):
    ws_current = web.WebSocketResponse()
    ws_ready = ws_current.can_prepare(request)
    if not ws_ready.ok:
        return aiohttp_jinja2.render_template('index.html', request, {})

    await ws_current.prepare(request)

    # name = get_random_name()
    name = str(uuid.uuid4())
    log.info('%s joined.', name)

    await ws_current.send_json({'action': 'connect', 'name': name})

    for ws in request.app['websockets'].values():
        await ws.send_json({'action': 'join', 'name': name})
    request.app['websockets'][name] = ws_current

    while True:
        msg = await ws_current.receive()

        if msg.type == aiohttp.WSMsgType.text:
            for ws in request.app['websockets'].values():
                if ws is not ws_current:
                    await ws.send_json(
                        {'action': 'sent', 'name': name, 'text': msg.data})
        else:
            break

    del request.app['websockets'][name]
    log.info('%s disconnected.', name)
    for ws in request.app['websockets'].values():
        await ws.send_json({'action': 'disconnect', 'name': name})

    return ws_current


async def create_callback(request):

    if request.method == 'POST':
        data = await request.post()
        url = data['url']
        ts = data['ts']
        print('submitted', url, ts)
        # TODO real username here
        insert(config, url, ts, 'demouser')

    callbacks = read_callbacks(config, 'demouser')
    print('found %i callbacks' % len(callbacks))
    # [print(callback) for callback in callbacks]

    return aiohttp_jinja2.render_template('create_callback.html', request, {'callbacks': callbacks})


async def show_config(request):
    msg = 'config is %s' % config
    print(msg)
    return web.Response(text=msg)

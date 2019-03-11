import logging
import aiohttp
import aiohttp_jinja2
from aiohttp import web
from callbacksweb.db import insert
import uuid
from callbacksweb.config import DevConfig, ProdConfig
import os
import datetime
from .util import getself


config = DevConfig
if 'DO_PROD' in os.environ:
    config = ProdConfig


log = logging.getLogger(__name__)


async def handle(request):
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

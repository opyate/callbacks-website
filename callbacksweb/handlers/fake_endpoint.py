import logging
import aiohttp
from aiohttp import web
from .util import getself

log = logging.getLogger(__name__)


async def handle(request):
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

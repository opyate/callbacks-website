import logging
from aiohttp import web


log = logging.getLogger(__name__)


async def handle(request):
    raise web.HTTPFound('https://cb.uys.io')

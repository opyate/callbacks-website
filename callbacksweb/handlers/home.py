import logging
import aiohttp_jinja2


log = logging.getLogger(__name__)


async def handle(request):
    return aiohttp_jinja2.render_template('index.html', request, {})

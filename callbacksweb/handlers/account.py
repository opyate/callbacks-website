#import aiohttp
import aiohttp_jinja2


async def handle(request):
    return aiohttp_jinja2.render_template('account.html', request, {})

import logging

import jinja2

import aiohttp_jinja2
from aiohttp import web
from callbacksweb.views import index, create_callback

import sys
for key, val in sys.modules.items():
    print(key, val)

# from https://aiohttp-demos.readthedocs.io/en/latest/index.html#aiohttp-demos-polls-beginning
async def init_app():

    app = web.Application()

    app['websockets'] = {}

    app.on_shutdown.append(shutdown)

    aiohttp_jinja2.setup(
        app, loader=jinja2.PackageLoader('callbacksweb', 'templates'))

    app.router.add_get('/', index)
    app.router.add_get('/new', create_callback)

    return app


async def shutdown(app):
    for ws in app['websockets'].values():
        await ws.close()
    app['websockets'].clear()


def main():
    logging.basicConfig(level=logging.DEBUG)

    app = init_app()
    web.run_app(app)


if __name__ == '__main__':
    main()

import logging
import os
import jinja2
import ssl
import aiohttp_jinja2
from aiohttp import web
from callbacksweb.views import index, create_callback, fake_endpoint


# from https://aiohttp-demos.readthedocs.io/en/latest/index.html#aiohttp-demos-polls-beginning
async def init_app():

    app = web.Application()

    app['websockets'] = {}

    app.on_shutdown.append(shutdown)

    aiohttp_jinja2.setup(
        app, loader=jinja2.PackageLoader('callbacksweb', 'templates'))

    app.router.add_get('/', index)
    app.router.add_get('/new', create_callback)
    app.router.add_post('/new', create_callback)
    app.router.add_get('/api', fake_endpoint)
    app.router.add_post('/api', fake_endpoint)


    return app


async def shutdown(app):
    for ws in app['websockets'].values():
        await ws.close()
    app['websockets'].clear()


def main():
    logging.basicConfig(level=logging.DEBUG)

    app = init_app()

    if 'DO_PROD' in os.environ:
        # prod
        ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ssl_context.load_cert_chain('/opt/cert/cert.pem', '/opt/cert/key.pem')
        web.run_app(app, ssl_context=ssl_context, port=443)
    else:
        # dev
        web.run_app(app=app, port=80)


if __name__ == '__main__':
    main()

import logging
import jinja2
import aiohttp_jinja2
from aiohttp import web
from callbacksweb.handlers import callbacks, home, users
import aiohttp_cors
from callbacksweb.auth import unpack_jwt


# from https://aiohttp-demos.readthedocs.io/en/latest/index.html#aiohttp-demos-polls-beginning
async def init_app():

    app = web.Application(middlewares=[unpack_jwt])

    cors = aiohttp_cors.setup(
        app,
        defaults={
            "*":
            aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*")
        }
    )

    app['websockets'] = {}

    app.on_shutdown.append(shutdown)

    aiohttp_jinja2.setup(
        app, loader=jinja2.PackageLoader('callbacksweb', 'templates'))

    app.router.add_get('/', home.handle)

    cors.add(app.router.add_get('/callbacks', callbacks.handle))
    cors.add(app.router.add_post('/callbacks', callbacks.handle))
    cors.add(app.router.add_get('/users', users.handle))

    # app.router.add_get('/meta', show_config)

    # app.router.add_static('/static/', path=str('static'))

    return app


async def shutdown(app):
    for ws in app['websockets'].values():
        await ws.close()
    app['websockets'].clear()


def main():
    logging.basicConfig(level=logging.DEBUG)

    app = init_app()

    web.run_app(app=app)


if __name__ == '__main__':
    main()

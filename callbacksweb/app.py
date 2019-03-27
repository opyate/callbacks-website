import logging
from aiohttp import web
from callbacksweb.handlers import callbacks, home, users
import aiohttp_cors
from callbacksweb.auth import unpack_jwt, unpack_api_key


# from https://aiohttp-demos.readthedocs.io/en/latest/index.html#aiohttp-demos-polls-beginning
async def init_app():

    app = web.Application(middlewares=[unpack_jwt, unpack_api_key])

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

    cors.add(app.router.add_get('/callbacks/{id}', callbacks.handle))
    cors.add(app.router.add_delete('/callbacks/{id}', callbacks.handle))
    cors.add(app.router.add_get('/callbacks', callbacks.handle))
    cors.add(app.router.add_post('/callbacks', callbacks.handle))
    cors.add(app.router.add_get('/users', users.handle))

    app.router.add_get('/{tail:.*}', home.handle)

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

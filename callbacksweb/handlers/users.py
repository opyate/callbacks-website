import logging
from aiohttp import web
from callbacksweb.db import read_user, insert_user
from callbacksweb.config import DevConfig, ProdConfig
import os
import sys, traceback
import string
import random
from callbacksweb.handlers.util import js


config = DevConfig
if 'DO_PROD' in os.environ:
    config = ProdConfig

log = logging.getLogger(__name__)


async def handle(request):
    # non-auth user is not allowed to do anything
    # demo user is allowed to use cbapi.uys.io/test as a url
    # anyone else can use anything else

    try:
        apikey = None

        if request.method == 'GET':
            user = read_user(config, request['uid'])

            if user:
                return web.json_response(js(user))
            else:
                # create a user with an API key, then return it
                letters = string.ascii_letters
                letters += string.digits
                api_key = ''.join(random.choice(letters) for i in range(42))
                user = insert_user(config, request['uid'], api_key)
                return web.json_response(js(user))

    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        return web.Response(text='Something went wrong :(', status=500)
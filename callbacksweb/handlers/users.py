import logging
from aiohttp import web
from callbacksweb.db import read_user, insert_user
from callbacksweb.config import DevConfig, ProdConfig
import os
import sys, traceback
import string
import random
from callbacksweb.handlers.util import js
import uuid


config = DevConfig
if 'DO_PROD' in os.environ:
    config = ProdConfig

log = logging.getLogger(__name__)


async def handle(request):
    try:
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
        correlation_id = str(uuid.uuid4())
        print(correlation_id)
        traceback.print_exc(file=sys.stdout)
        return web.json_response({
            'message': 'Something went wrong :(',
            'correlation_id': correlation_id
        }, status=500)
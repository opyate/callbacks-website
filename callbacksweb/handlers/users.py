import logging
from aiohttp import web
from callbacksweb.db import read_user
from callbacksweb.config import DevConfig, ProdConfig
import os
import base64
import sys, traceback
import jsonpickle
import json


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
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            access_token = auth_header.replace('Bearer ', '')
            print('got access token', access_token)

        if request.method == 'GET':
            # TODO get username from JWT
            user = read_user(config, 'demouser')

            data = json.loads(jsonpickle.encode(user))
            data.pop('py/object')
            return web.json_response(data)
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        return web.Response(text='Something went wrong :(', status=500)
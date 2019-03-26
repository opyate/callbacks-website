from jose import jwt
from aiohttp.web import middleware
import aiohttp
from callbacksweb.config import DevConfig, ProdConfig
import os
import base64
from callbacksweb.db import read_user_by_api_key


config = DevConfig
if 'DO_PROD' in os.environ:
    config = ProdConfig


async def fetch(session, url):
    async with session.get(url, verify_ssl=False) as response:
        return await response.json()

@middleware
async def unpack_jwt(request, handler):
    if 'Authorization' in request.headers:
        auth_header = request.headers['Authorization']
        if 'Bearer' in auth_header:
            all_tokens = auth_header.replace('Bearer ', '')

            id_token, access_token = all_tokens.split('::')
            print('got token', id_token)
            uid = await get_user_id(id_token, access_token)
            print('uid', uid)
            request['uid'] = uid

    resp = await handler(request)
    return resp


async def get_user_id(token, access_token):
    async with aiohttp.ClientSession() as session:
        url = "https://{}/.well-known/jwks.json".format(config.AUTH0_DOMAIN)
        jwks = await fetch(session, url)

        unverified_header = jwt.get_unverified_header(token)

        rsa_key = {}
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }
        if rsa_key:

            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=unverified_header["alg"],
                audience=config.API_ID,
                issuer='https://{}/'.format(config.AUTH0_DOMAIN),
                access_token=access_token
            )

            return payload['sub']
    return None


@middleware
async def unpack_api_key(request, handler):
    if 'Authorization' in request.headers:
        auth_header = request.headers['Authorization']
        if 'Basic' in auth_header:
            basic_encoded = auth_header.replace('Basic ', '')
            api_key = base64.b64decode(basic_encoded).decode('utf-8').replace(':', '')

            user = read_user_by_api_key(config, api_key)
            request['uid'] = user.user_id

    resp = await handler(request)
    return resp
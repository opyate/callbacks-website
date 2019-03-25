import jsonpickle
import json


def getself(request):
    host = request.host
    scheme = request.scheme
    return '{}://{}'.format(scheme, host)


def js(thing):
    data = json.loads(jsonpickle.encode(thing))
    data.pop('py/object')
    return data
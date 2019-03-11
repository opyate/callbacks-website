def getself(request):
    host = request.host
    scheme = request.scheme
    return '{}://{}'.format(scheme, host)

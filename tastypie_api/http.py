import json
from django.http import HttpResponse


SUCCESS = 0
FAILED = 1
DEFAULT_MSG = {SUCCESS: 'SUCCESS', FAILED: 'FAILED', 404: "Not found", 401: "Unauthorized", 403: "No permisson", 405: "Method not be permitted"}


class Result(HttpResponse):
    res_code = SUCCESS

    def __init__(self, data={}, msg=None, status=None, meta={}, content_type='application/json'):

        status_code = status or self.res_code

        msg = msg or DEFAULT_MSG.get(status_code, DEFAULT_MSG[FAILED])

        wrapped_data = {'status_code': status_code, 'msg': msg, 'meta': meta, 'data': data}
        wrapped_data = json.dumps(wrapped_data)
        super(Result, self).__init__(wrapped_data, content_type=content_type)


class FailedResult(Result):
    res_code = FAILED


class HttpCreated(Result):
    res_code = SUCCESS

    def __init__(self, *args, **kwargs):
        location = kwargs.pop('location', '')

        super(HttpCreated, self).__init__(*args, **kwargs)
        self['Location'] = location


class HttpAccepted(Result):
    res_code = SUCCESS


class HttpNoContent(Result):
    res_code = SUCCESS


class HttpMultipleChoices(HttpResponse):
    status_code = 300


class HttpSeeOther(HttpResponse):
    status_code = 303


class HttpNotModified(HttpResponse):
    status_code = 304


class HttpBadRequest(FailedResult):
    res_code = 400


class HttpUnauthorized(FailedResult):
    res_code = 401


class HttpForbidden(FailedResult):
    res_code = 403


class HttpNotFound(FailedResult):
    res_code = 404


class HttpMethodNotAllowed(FailedResult):
    res_code = 405


class HttpNotAcceptable(FailedResult):
    res_code = 406


class HttpConflict(FailedResult):
    res_code = 409


class HttpGone(FailedResult):
    res_code = 410


class HttpUnsupportedMediaType(FailedResult):
    res_code = 415


class HttpUnprocessableEntity(HttpResponse):
    res_code = 422


class HttpTooManyRequests(FailedResult):
    res_code = 429


class HttpApplicationError(HttpResponse):
    status_code = 500


class HttpNotImplemented(HttpResponse):
    status_code = 501

import json
from django.http import HttpResponse

"""
自定义response数据格式
The various HTTP responses for use in returning proper HTTP codes.
"""

SUCCESS = 0
FAILED = 1
DEFAULT_MSG = {
    SUCCESS: 'SUCCESS',
    FAILED: 'FAILED'
}


class Result(HttpResponse):
    """
    对返回的数据进行封装，返回码res_code --> 0:SUCCESS, 1:FAILED
    """
    # 这里如果命名为status_code会直接影响到响应的状态码
    res_code = SUCCESS

    def __init__(self, data={}, msg=None, status=None, meta={}, content_type='application/json'):

        status_code = status or self.res_code
        msg = msg or DEFAULT_MSG[status_code]

        wrapped_data = {
            'status_code': status_code,
            'msg': msg,
            'meta': meta,
            'data': data
        }
        wrapped_data = json.dumps(wrapped_data)
        super(Result, self).__init__(wrapped_data,
                                     content_type=content_type)


class FailedResult(Result):
    """
    所有预期的异常结果由此函数返回，传递错误信息msg即可
    """
    res_code = FAILED


class HttpCreated(HttpResponse):
    res_code = 201

    def __init__(self, *args, **kwargs):
        location = kwargs.pop('location', '')

        super(HttpCreated, self).__init__(*args, **kwargs)
        self['Location'] = location


class HttpAccepted(HttpResponse):
    res_code = 202


class HttpNoContent(HttpResponse):
    res_code = 204

    def __init__(self, *args, **kwargs):
        super(HttpNoContent, self).__init__(*args, **kwargs)
        del self['Content-Type']


class HttpMultipleChoices(HttpResponse):
    res_code = 300


class HttpSeeOther(HttpResponse):
    res_code = 303


class HttpNotModified(HttpResponse):
    res_code = 304


class HttpBadRequest(HttpResponse):
    res_code = 400


class HttpUnauthorized(HttpResponse):
    res_code = 401


class HttpForbidden(FailedResult):
    res_code = 403


class HttpNotFound(HttpResponse):
    res_code = 404


class HttpMethodNotAllowed(HttpResponse):
    res_code = 405


class HttpConflict(HttpResponse):
    res_code = 409


class HttpGone(HttpResponse):
    res_code = 410


class HttpUnprocessableEntity(HttpResponse):
    res_code = 422


class HttpTooManyRequests(HttpResponse):
    res_code = 429


class HttpApplicationError(HttpResponse):
    res_code = 500


class HttpNotImplemented(FailedResult):
    res_code = 501

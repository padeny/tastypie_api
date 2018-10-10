from django.contrib.auth.models import User
from django.contrib.sessions.models import Session

from tastypie.authentication import SessionAuthentication as SessAuth
from tastypie.compat import is_authenticated

from mas_tastypie_api.http import FailedResult


class SessionAuthentication(SessAuth):
    def __init__(self, *args, **kwargs):
        super(SessionAuthentication, self).__init__(*args, **kwargs)

    def is_authenticated(self, request, **kwargs):
        # raw_result = is_authenticated(request.user)
        # if not raw_result:
        #     return FailedResult(msg="未登录认证")
        # return raw_result

        if 'sessionid' in request.COOKIES:
            s = Session.objects.filter(pk=request.COOKIES['sessionid']).first()
            if s and '_auth_user_id' in s.get_decoded():
                u = User.objects.filter(id=s.get_decoded()['_auth_user_id']).first()
                if u:
                    request.user = u
                    return True
        raw_result = is_authenticated(request.user)
        if not raw_result:
            return FailedResult(msg="未登录认证")
        return raw_result

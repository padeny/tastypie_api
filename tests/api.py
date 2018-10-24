from django.contrib.auth.models import User
from django.urls import re_path
from tastypie.authorization import Authorization
from tastypie.authentication import Authentication, BasicAuthentication, SessionAuthentication  # noqa
from tastypie.resources import fields
from tastypie.utils import trailing_slash
from tastypie.resources import ModelResource as t_ModelResource  # noqa

from mas_tastypie_api.decorators import custom_api
from mas_tastypie_api.resources import ModelResource  # noqa
from mas_tastypie_api.http import Result

from .models import Entry


class UserResource(ModelResource):
    class Meta:
        resource_name = "user"
        queryset = User.objects.all()
        authorization = Authorization()
        authentication = BasicAuthentication()


class EntryResource(ModelResource):
    user = fields.ForeignKey(to=UserResource, attribute='user', full=True, null=True)

    class Meta:
        resource_name = "entries"
        queryset = Entry.objects.all()
        include_resource_uri = False
        fields = ['created', 'slug', 'title', 'user', 'image']
        # paginator_class = Paginator
        authorization = Authorization()
        # authentication = Authentication()  # 默认 OnlyRead  post不被允许
        authentication = BasicAuthentication()  # tests中使用
        # authentication = SessionAuthentication()  # runserver 时使用

    def prepend_urls(self):
        return [
            re_path(
                r"(?P<resource_name>%s)/test_custom_api%s$" % (self._meta.resource_name, trailing_slash),
                self.wrap_view('test_custom_api'),
                name="api_custom_api"),
            re_path(
                r"(?P<resource_name>%s)/test_custom_api2%s$" % (self._meta.resource_name, trailing_slash),
                self.wrap_view('test_custom_api2'),
                name="api_custom_api2"),
            re_path(
                r"(?P<resource_name>%s)/test_custom_api3%s$" % (self._meta.resource_name, trailing_slash),
                self.wrap_view('test_custom_api3'),
                name="api_custom_api3"),
            re_path(
                r"(?P<resource_name>%s)/test_custom_api4%s$" % (self._meta.resource_name, trailing_slash),
                self.wrap_view('test_custom_api4'),
                name="api_custom_api4"),
        ]

    @custom_api(allowed=["get"], login_required=True)
    def test_custom_api(self, request, **kwargs):
        data = {"api": "api"}
        return Result(data=data)

    @custom_api(allowed=["get"], login_required=False)
    def test_custom_api2(self, request, **kwargs):
        data = {"api2": "api2"}
        return Result(data=data)

    @custom_api(allowed=["get", "post"], login_required=False)
    def test_custom_api3(self, request, **kwargs):
        data = {"apia": "apia"}
        return Result(data=data)

    def test_custom_api4(self, request, **kwargs):
        data = {"apia": "apia"}
        return Result(data=data)

    # def get_list(self, request, **kwargs):
    # return super(EntryResource, self).get_list(request, **kwargs)

    # def post_list(self, request, **kwargs):
    #     import pdb
    #     pdb.set_trace()
    #     return super(EntryResource, self).post_list(request, **kwargs)


class Entry2Resource(ModelResource):
    user = fields.ForeignKey(to=UserResource, attribute='user', full=True, null=True)

    class Meta:
        resource_name = "entries2"
        queryset = Entry.objects.all()
        include_resource_uri = False
        fields = ['created', 'slug', 'title', 'user', 'image']
        # paginator_class = Paginator
        authorization = Authorization()
        # authentication = Authentication()  # 默认 OnlyRead  post不被允许
        # authentication = BasicAuthentication()  # tests中使用
        authentication = SessionAuthentication()  # runserver 时使用

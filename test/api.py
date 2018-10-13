from django.contrib.auth.models import User

from tastypie.authorization import Authorization
from tastypie.authentication import BasicAuthentication, SessionAuthentication  # noqa
from tastypie.resources import fields
from tastypie.resources import ModelResource as t_ModelResource  # noqa

from mas_tastypie_api.resources import ModelResource  # noqa
from mas_tastypie_api.paginator import Paginator

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
        paginator_class = Paginator
        authorization = Authorization()
        authentication = BasicAuthentication()
        # authentication = SessionAuthentication()

    # def get_list(self, request, **kwargs):
    #     print("das")
    #     import pdb
    #     pdb.set_trace()
    #     return super(EntryResource, self).get_list(request, **kwargs)

    # def post_list(self, request, **kwargs):
    #     import pdb
    #     pdb.set_trace()
    #     return super(EntryResource, self).post_list(request, **kwargs)

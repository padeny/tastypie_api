from django.contrib.auth.models import User

from tastypie.authorization import Authorization
from tastypie.authentication import BasicAuthentication, SessionAuthentication  # noqa
from tastypie.resources import fields
from tastypie.resources import ModelResource as t_ModelResource  # noqa

from mas_tastypie_api.http import Result, FailedResult  # noqa
from mas_tastypie_api.resources import ModelResource  # noqa
from mas_tastypie_api.exceptions import DataFormatError  # noqa

from .models import Author, Article, Entry


class AuthorReousrce(ModelResource):
    class Meta:
        queryset = Author.objects.all()
        resource_name = 'authors'
        class_name = Author
        # include_resource_uri = False
        always_return_data = True
        authorization = Authorization()
        authentication = BasicAuthentication()


class ArticleResource(ModelResource):
    author = fields.ForeignKey(to=AuthorReousrce, attribute='author')

    class Meta:
        queryset = Article.objects.all()
        resource_name = 'articles'
        class_name = Article
        # include_resource_uri = False
        always_return_data = True
        fields = ['title', 'author']
        authorization = Authorization()
        authentication = BasicAuthentication()

    # def get_list(self, request, **kwargs):
    #     print("das")
    #     return super(ArticleResource, self).get_list(request, **kwargs)


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
        authorization = Authorization()
        # authentication = BasicAuthentication()
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

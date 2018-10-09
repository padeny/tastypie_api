from tastypie.authorization import Authorization
# from tastypie.resources import ModelResource

from mas_tastypie_api.authentication import SessionAuthentication

from mas_tastypie_api import http
from mas_tastypie_api.http import Result, FailedResult
from mas_tastypie_api.resources import ModelResource
from mas_tastypie_api.exceptions import DataFormatError

from .models import Article


class ArticleResource(ModelResource):
    # profile = fields.ForeignKey(to='profiles.api.ProfilesResource', attribute='profile')

    class Meta:
        queryset = Article.objects.all()
        resource_name = 'article'
        class_name = Article
        # include_resource_uri = False
        always_return_data = True
        allowed_methods = ['get', 'patch', 'post']
        limit = 20
        fields = ['title', 'author']
        authorization = Authorization()
        # authentication = SessionAuthentication()

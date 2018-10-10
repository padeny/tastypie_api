from tastypie.authorization import Authorization
# from tastypie.resources import ModelResource

from mas_tastypie_api.authentication import SessionAuthentication  # noqa

from mas_tastypie_api.http import Result, FailedResult  # noqa
from mas_tastypie_api.resources import ModelResource  # noqa
from mas_tastypie_api.exceptions import DataFormatError  # noqa

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

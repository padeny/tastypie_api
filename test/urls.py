from django.contrib import admin
from django.urls import path, include
from tastypie.api import Api  # noqa
from tastypie.api import NamespacedApi
from .api import ArticleResource, EntryResource
from . import views

# v1_api = Api(api_name='v1')
v1_api = NamespacedApi(api_name='v1', urlconf_namespace='test')
v1_api.register(ArticleResource())
v1_api.register(EntryResource())

urlpatterns = [
    path('admin/', admin.site.urls),
    path('atest/', views.atest),
    path('api/', include((v1_api.urls, 'test'), namespace='test')),
]

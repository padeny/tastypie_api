from django.contrib import admin
from django.urls import path, include
from tastypie.api import Api
from .api import ArticleResource
from . import views

# v1_api = NamespacedApi(api_name='v1', urlconf_namespace='accounts')
v1_api = Api(api_name='v1')
v1_api.register(ArticleResource())

urlpatterns = [
        path('admin/', admin.site.urls),
        path('atest/', views.atest),
        path('api/', include(v1_api.urls)),
]

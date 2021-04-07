# from django.contrib import admin
from django.urls import path, include
from tastypie.api import Api  # noqa
from tastypie.api import NamespacedApi  # noqa: flake8
from .api import EntryResource, Entry2Resource
v1_api = Api(api_name='v1')
# v1_api = NamespacedApi(api_name='v1', urlconf_namespace='tests')
v1_api.register(EntryResource())
v1_api.register(Entry2Resource())

urlpatterns = [
    # path('admin/', admin.site.urls),
    # path('api/', include((v1_api.urls, 'tests'), namespace='tests')),
    path('api/', include(v1_api.urls)),
]

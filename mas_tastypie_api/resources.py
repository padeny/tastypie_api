import json
from django.db.utils import IntegrityError

from django.core.exceptions import (ValidationError)
from django.conf import settings
from django.utils import six
from django.http import HttpResponse
from django.utils.cache import patch_cache_control, patch_vary_headers
from django.views.decorators.csrf import csrf_exempt

from tastypie import fields
from tastypie.exceptions import (BadRequest, ImmediateHttpResponse)
from tastypie.compat import reverse
from tastypie import resources
from tastypie.resources import (sanitize, ResourceOptions, ModelDeclarativeMetaclass, convert_post_to_VERB)
from tastypie.resources import Resource as t_Resource, BaseModelResource as t_BaseModelResource

from tastypie import authentication

from mas_tastypie_api import http
from mas_tastypie_api.paginator import Paginator
from mas_tastypie_api.http import FailedResult, Result
from mas_tastypie_api.exceptions import DataFormatError


def convert_post_to_patch(request):
    request.body
    request._read_started = False
    return convert_post_to_VERB(request, verb='PATCH')


def convert_post_to_put(request):
    request.body
    request._read_started = False
    return convert_post_to_VERB(request, verb='PUT')


class NewResourceOptions(ResourceOptions):
    paginator_class = Paginator


# monkey-patch
resources.http = http
authentication.HttpUnauthorized = http.HttpUnauthorized
resources.convert_post_to_patch = convert_post_to_patch
resources.convert_post_to_put = convert_post_to_put
resources.ResourceOptions = NewResourceOptions


# class Resource(six.with_metaclass(DeclarativeMetaclass, t_Resource)):
class Resource(t_Resource):
    """
    """

    def wrap_view(self, view):
        @csrf_exempt
        def wrapper(request, *args, **kwargs):
            try:
                callback = getattr(self, view)
                response = callback(request, *args, **kwargs)

                varies = getattr(self._meta.cache, "varies", [])

                if varies:
                    patch_vary_headers(response, varies)

                if self._meta.cache.cacheable(request, response):
                    if self._meta.cache.cache_control():
                        patch_cache_control(response, **self._meta.cache.cache_control())

                if request.is_ajax() and not response.has_header("Cache-Control"):
                    patch_cache_control(response, no_cache=True)
                return response

            except IntegrityError as e:
                return FailedResult(msg=str(e))
            # =========except custome exception=========
            except DataFormatError as e:
                return FailedResult(msg=e.msg)
            # ==========================================
            except (BadRequest, fields.ApiFieldError) as e:
                # data = {"error": sanitize(e.args[0]) if getattr(e, 'args') else ''}
                # =========except custome exception=========
                return FailedResult(msg=sanitize(e.args[0]) if getattr(e, 'args') else '')
                # return self.error_response(request, data, response_class=http.HttpBadRequest)
                # ==========================================
            except ValidationError as e:
                # data = {"error": sanitize(e.messages)}
                # =========except custome exception=========
                return FailedResult(msg=sanitize(e.messages))
                # return self.error_response(request, data, response_class=http.HttpBadRequest)
                # ==========================================
            except Exception as e:
                if hasattr(e, 'response') and isinstance(e.response, HttpResponse):
                    # =========except custome exception=========
                    return e.response
                # ==========================================

                if settings.DEBUG and getattr(settings, 'TASTYPIE_FULL_DEBUG', False):
                    raise
                if request.META.get('SERVER_NAME') == 'testserver':
                    raise
                return self._handle_500(request, e)

        return wrapper

    def method_check(self, request, allowed=None):
        """
        补充提示信息
        """
        if allowed is None:
            allowed = []

        request_method = request.method.lower()
        allows = "allowd methods must be in: " + ','.join([meth.upper() for meth in allowed])

        if request_method == "options":
            response = HttpResponse(allows)
            response['Allow'] = allows
            raise ImmediateHttpResponse(response=response)

        if request_method not in allowed:
            response = http.HttpMethodNotAllowed(allows)
            response['Allow'] = allows
            raise ImmediateHttpResponse(response=response)

        return request_method

    def deserialize(self, request, data, format=None):
        "支持uploadfile"
        format = format.split(';')[0] if format else request.META.get('CONTENT_TYPE', 'application/json')

        if format == 'application/x-www-form-urlencoded':
            data = request.POST.copy()
            deserialized = data.dict()

        elif format.startswith('multipart'):
            data = request.POST.copy()
            data.update(request.FILES)
            deserialized = data.dict()
        else:
            deserialized = self._meta.serializer.deserialize(data, format=request.META.get('CONTENT_TYPE', format))

        return deserialized

    def create_response(self, request, data, **kwargs):
        """
            自定义输出格式
        """
        serialized = self.serialize(request, data, "application/json")
        deserialized = json.loads(serialized)
        if self._meta.collection_name in deserialized and \
           isinstance(deserialized[self._meta.collection_name], list):
            return Result(meta=deserialized['meta'], data=deserialized[self._meta.collection_name])
        return Result(data=deserialized)


class BaseModelResource(t_BaseModelResource, Resource):
    pass


class ModelResource(six.with_metaclass(ModelDeclarativeMetaclass, BaseModelResource)):
    ''
    pass


class NamespacedModelResource(ModelResource):
    """
    A ModelResource subclass that respects Django namespaces.
    """

    def _build_reverse_url(self, name, args=None, kwargs=None):
        namespaced = "%s:%s" % (self._meta.urlconf_namespace, name)
        return reverse(namespaced, args=args, kwargs=kwargs)

import json
from django.db.utils import IntegrityError

from tastypie.resources import Resource, DeclarativeMetaclass, BaseModelResource, ModelDeclarativeMetaclass

from django.core.exceptions import (
    ObjectDoesNotExist,
    ValidationError,
)
from django.conf import settings
from django.utils import six
from django.http import HttpResponse, Http404
from django.utils.cache import patch_cache_control, patch_vary_headers
from django.utils.html import escape
from django.views.decorators.csrf import csrf_exempt

from tastypie import fields
from tastypie.exceptions import (
    NotFound,
    BadRequest,
    UnsupportedFormat,
    UnsupportedSerializationFormat,
    UnsupportedDeserializationFormat,
)
from tastypie.compat import reverse
from tastypie import http as t_http

from mas_tastypie_api import http
from mas_tastypie_api.http import FailedResult, Result
from mas_tastypie_api.exceptions import DataFormatError


def sanitize(text):
    # We put the single quotes back, due to their frequent usage in exception
    # messages.
    return escape(text).replace('&#39;', "'").replace('&quot;', '"')


class Resource(six.with_metaclass(DeclarativeMetaclass, Resource)):
    """
    #TODO
    1.checkparam
    2.check fields which can not be null
    3.customc urls
  √ 4.union response-format,e.g Result or FailedResult
    5.overwrite wrap_view() to return union response-format for some Exception
    """

    # class Meta:
    #     #serializer = Serializer()
    #     object_class = None

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
                return self.get_custome_response_class(response)
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
                    return self.get_custome_response_class(e.response)
                # ==========================================

                if settings.DEBUG and getattr(settings, 'TASTYPIE_FULL_DEBUG', False):
                    raise
                if request.META.get('SERVER_NAME') == 'testserver':
                    raise
                return self._handle_500(request, e)

        return wrapper

    def get_custome_response_class(self, response):
        """
        Can be overridden to customize response classes.
        Should always return a subclass of ``django.http.HttpResponse``.
        """
        if isinstance(response, (t_http.HttpCreated, t_http.HttpAccepted, t_http.HttpNoContent)):
            return http.Result()
        elif response.status_code > 299:
            msg = response.content.decode() if response.content else None
            return http.FailedResult(msg=msg, status=response.status_code)
        else:
            return response

    def get_response_class_for_exception(self, request, exception):
        """
        Can be overridden to customize response classes used for uncaught
        exceptions. Should always return a subclass of
        ``django.http.HttpResponse``.
        """
        if isinstance(exception, (NotFound, ObjectDoesNotExist, Http404)):
            return http.HttpNotFound
        elif isinstance(exception, UnsupportedSerializationFormat):
            return http.HttpNotAcceptable
        elif isinstance(exception, UnsupportedDeserializationFormat):
            return http.HttpUnsupportedMediaType
        elif isinstance(exception, UnsupportedFormat):
            return http.HttpBadRequest

        return http.HttpApplicationError

    def save(self, bundle, skip_errors=False):
        try:
            return super(Resource, self).save(bundle, skip_errors=skip_errors)
        except IntegrityError as e:
            raise DataFormatError(msg=str(e))

    def is_valid(self, bundle):
        """
        Handles checking if the data provided by the user is valid.

        Mostly a hook, this uses class assigned to ``validation`` from
        ``Resource._meta``.

        If validation fails, an error is raised with the error messages
        serialized inside it.
        """
        errors = self._meta.validation.is_valid(bundle, bundle.request)

        if errors:
            # =========except custome exception=========
            # bundle.errors[self._meta.resource_name] = errors
            bundle.errors = errors
            # ========================================
            return False

        return True

    def deserialize(self, request, data, format=None):
        "支持uploadfile"
        if not format:
            format = request.META.get('CONTENT_TYPE', 'application/json')

        format = format.split(';')[0]

        if format == 'application/x-www-form-urlencoded':
            return request.POST

        if format.startswith('multipart'):
            data = request.POST.copy()
            data.update(request.FILES)
            return data
        return super(Resource, self).deserialize(request, data, format)

    def create_response(self, request, data, **kwargs):
        """
            自定义输出格式
        """
        # import pdb;pdb.set_trace()
        serialized = self.serialize(request, data, "application/json")
        deserialized = json.loads(serialized)
        if self._meta.collection_name in deserialized and \
           isinstance(deserialized[self._meta.collection_name], list):
            return Result(meta=deserialized['meta'], data=deserialized[self._meta.collection_name])
        return Result(data=deserialized)


class BaseModelResource(BaseModelResource, Resource):
    pass


class ModelResource(six.with_metaclass(ModelDeclarativeMetaclass, BaseModelResource)):
    def _build_reverse_url(self, name, args=None, kwargs=None):
        """
        A ModelResource subclass that respects Django namespaces.
        """
        namespaced = "%s:%s" % (self._meta.urlconf_namespace, name)
        return reverse(namespaced, args=args, kwargs=kwargs)

from django.utils import six
try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode

from tastypie.paginator import Paginator as t_Paginator

from mas_tastypie_api.exceptions import DataFormatError


class Paginator(t_Paginator):
    def __init__(self,
                 request_data,
                 objects,
                 resource_uri=None,
                 limit=None,
                 offset=0,
                 max_limit=1000,
                 collection_name='objects'):
        """
        Instantiates the ``Paginator`` and allows for some configuration.

        The ``request_data`` argument ought to be a dictionary-like object.
        May provide ``limit`` and/or ``offset`` to override the defaults.
        Commonly provided ``request.GET``. Required.

        The ``objects`` should be a list-like object of ``Resources``.
        This is typically a ``QuerySet`` but can be anything that
        implements slicing. Required.

        Optionally accepts a ``limit`` argument, which specifies how many
        items to show at a time. Defaults to ``None``, which is no limit.

        Optionally accepts an ``offset`` argument, which specifies where in
        the ``objects`` to start displaying results from. Defaults to 0.

        Optionally accepts a ``max_limit`` argument, which the upper bound
        limit. Defaults to ``1000``. If you set it to 0 or ``None``, no upper
        bound will be enforced.
        """
        self.request_data = request_data
        self.objects = objects
        self.limit = limit
        self.max_limit = max_limit
        self.offset = offset
        self.resource_uri = resource_uri
        self.collection_name = collection_name

    def get_page_num(self):
        """
        It is optional, which determines which page_num results to return.

        It attempts to use the user-provided ``page_num`` from the GET parameters,
        if specified and ignore ``offset`` parameter.
        """

        page_num = self.request_data.get('page_num', 1)
        try:
            page_num = int(page_num)
        except ValueError:
            raise DataFormatError("Invalid page_num '%s' provided. Please provide an integer." % page_num)

        if page_num < 0:
            raise DataFormatError("Invalid page_num '%s' provided. Please provide a positive integer >= 0." % page_num)

        return page_num

    def get_slice(self, limit, page_num=1):
        """
        Slices the result set to the specified ``limit`` & ``offset``.
        """
        index = max((page_num - 1), 0) * limit

        if limit == 0:
            return self.objects[index:]

        return self.objects[index:index + limit]

    def _page_num_to_offset(self, limit, page_num):
        return max((page_num - 1), 0) * limit

    def _offset_to_page_num(self, limit, offset):
        return int(offset / limit) + 1

    def _generate_uri(self, limit, offset):
        if self.resource_uri is None:
            return None
        page_num = self._offset_to_page_num(limit, offset)
        try:
            # QueryDict has a urlencode method that can handle multiple values for the same key
            request_params = self.request_data.copy()
            if 'limit' in request_params:
                del request_params['limit']
            if 'page_num' in request_params:
                del request_params['page_num']
            request_params.update({'limit': limit, 'page_num': page_num})
            encoded_params = request_params.urlencode()
        except AttributeError:
            request_params = {}

            for k, v in self.request_data.items():
                if isinstance(v, six.text_type):
                    request_params[k] = v.encode('utf-8')
                else:
                    request_params[k] = v

            if 'limit' in request_params:
                del request_params['limit']
            if 'page_num' in request_params:
                del request_params['page_num']
            request_params.update({'limit': limit, 'page_num': page_num})
            encoded_params = urlencode(request_params)

        return '%s?%s' % (self.resource_uri, encoded_params)

    def page(self):
        """
        Generates all pertinent data about the requested page.

        Handles getting the correct ``limit`` & ``offset``, then slices off
        the correct set of results and returns all pertinent metadata.
        """
        limit = self.get_limit()
        page_num = self.get_page_num()
        offset = self._page_num_to_offset(limit, page_num)
        count = self.get_count()
        objects = self.get_slice(limit, page_num=page_num)
        meta = {
            'limit': limit,
            'page_num': page_num,
            'total_count': count,
        }

        if limit:
            meta['previous'] = self.get_previous(limit, offset)
            meta['next'] = self.get_next(limit, offset, count)

        return {
            self.collection_name: objects,
            'meta': meta,
        }

from django.utils import six
try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode

from tastypie.paginator import Paginator as t_Paginator

from tastypie_api.exceptions import DataFormatError


class Paginator(t_Paginator):

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
        objects = self.get_slice(limit, offset)
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

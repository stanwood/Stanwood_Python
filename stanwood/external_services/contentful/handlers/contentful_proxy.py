# The MIT License (MIT)
# 
# Copyright (c) 2018 stanwood GmbH
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
import logging

from stanwood.external_services.contentful.handlers.base import CustomBaseHandler
from stanwood.external_services.contentful.handlers.mixins.contentful_mixin import ContentfulMixin
from stanwood.handlers.mixins.cache import PublicCachingMixin


class ContentfulProxyBaseHander(PublicCachingMixin, ContentfulMixin, CustomBaseHandler):

    @property
    def folder(self):
        return 'assets'

    def get(self, item_type=None, item_id=None):
        """Get the content model of a space or get a single content type
        Reference: https://www.contentful.com/developers/docs/references/content-delivery-api
        """
        try:
            methods = self.types[item_type]
        except KeyError as key_error:
            logging.error("Unexpected item type `{}`".format(key_error))
            return self.abort(code=404)

        if item_id:
            response = methods[0](item_id)
        else:
            query = dict(self.request.params.items())
            logging.debug(query)
            response = methods[1](query)
        return self.response.write(response.content)

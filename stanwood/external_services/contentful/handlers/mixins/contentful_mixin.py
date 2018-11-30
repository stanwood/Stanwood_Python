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
import webapp2

from stanwood.external_services.contentful.utils.cached_contentful import cached_contentful


class ContentfulMixin(object):
    CONTENTFUL_SPACE = None
    CONTENTFUL_TOKEN = None
    APPLY_TRANSFORMATIONS = True

    @webapp2.cached_property
    def types(self):
        return {
            'content_types': [self.contentful.content_type, self.contentful.content_types],
            'entries': [self.contentful.entry, self.contentful.entries],
            'assets': [self.contentful.asset, self.contentful.assets],
            None: [self.contentful.root_endpoint, self.contentful.root_endpoint]
        }

    @webapp2.cached_property
    def contentful(self):
        return cached_contentful.Client(
            self.CONTENTFUL_SPACE,
            self.CONTENTFUL_TOKEN,
            raw_mode=True,
            content_type_cache=False,
            base_url=self.request.host_url,
            apply_transformations=self.APPLY_TRANSFORMATIONS
        )

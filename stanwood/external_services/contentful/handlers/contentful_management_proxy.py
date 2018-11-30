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
import webapp2

from google.appengine.api import urlfetch

from stanwood.handlers.mixins.cors import CorsMixin
from stanwood.firebase.decorators.firebase_token_required import firebase_token_required


class ContentfulManagementProxyBaseHandler(CorsMixin, webapp2.RequestHandler):

    CONTENTFUL = 'https://api.contentful.com/'
    CONTENTFUL_MANAGEMENT_TOKEN = None
    CONTENTFUL_SPACE = None

    @webapp2.cached_property
    def endpoint(self):
        return self.request.route_kwargs.pop('endpoint')

    @property
    def contentful_request(self):
        if self.endpoint[:6] != 'spaces':
            return u'spaces/{}/{}?{}'.format(
                self.CONTENTFUL_SPACE,
                self.endpoint,
                self.request.query_string
            )
        else:
            return u'{}?{}'.format(self.endpoint, self.request.query_string)

    @firebase_token_required({})
    def dispatch(self):
        if self.request.method != 'OPTIONS':
            logging.debug(
                u'{} {} \n{} \n{}'.format(
                    self.request.method,
                    self.contentful_request,
                    u'\n'.join(
                        u':'.join(value) for value in self.request.headers.items()
                    ),
                    self.request.body.decode('utf-8', errors='replace')
                )
            )

            headers = dict(self.request.headers.items())
            headers.update(
                {
                    'Authorization': 'Bearer {}'.format(self.CONTENTFUL_MANAGEMENT_TOKEN)
                }
            )

            response = urlfetch.fetch(
                self.CONTENTFUL + self.contentful_request,
                payload=self.request.body,
                method=self.request.method,
                headers=headers,
                deadline=60
            )

            logging.debug(u'{} \n {}'.format(
                response.status_code,
                response.content.decode('utf-8', errors='replace')
            ))
            response.headers.pop('content-length', None)
            self.response.headers = response.headers
            self.response.write(response.content)
            self.response.status_int = response.status_code
        else:
            super(ContentfulManagementProxyBaseHandler, self).dispatch()

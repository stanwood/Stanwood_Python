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
import json
import logging

import webapp2
from google.appengine.api import urlfetch


class ProxyError(Exception):
    def __init__(self, response):
        self.response = response


class ProxyHandler(webapp2.RequestHandler):
    BASE_URL = ''
    LOGGING = True
    DEADLINE = 60

    @property
    def path(self):
        try:
            url = '/{}'.format(
                self.request.route_args[0],
            )

            if self.request.query_string:
                url += '?' + self.request.query_string

            return url
        except IndexError:
            return self.request.path_qs

    def log_request(self):
        if self.LOGGING:
            logging.info(self.request.path_qs)
            logging.info(self.request.body)

    def log_response(self, response):
        if self.LOGGING:
            logging.info(response.status_code)
            logging.info(response.content)

    def dispatch(self):

        url = '{}{}'.format(
            self.BASE_URL,
            self.path,
        )

        self.log_request()

        try:
            response = urlfetch.fetch(
                url,
                deadline=self.DEADLINE,
                headers=self.request.headers,
                method=self.request.method,
                payload=self.request.body,
            )
            self.log_response(response)

            if response.status_code / 400:
                raise ProxyError(response)
        except Exception as e:
            self.handle_exception(e, self.app.debug)
        else:
            self.response.status_int = response.status_code
            self.response.headers = response.headers
            self.response.body = response.content

    def handle_exception(self, exception, debug):

        if isinstance(exception, ProxyError):
            self.response.status_int = exception.response.status_code
            self.response.body = exception.response.content
        else:
            raise exception

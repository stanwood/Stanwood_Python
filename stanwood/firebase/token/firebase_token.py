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

from jose import JWTError
from google.appengine.api import memcache
from google.appengine.api import urlfetch
from webob.cachecontrol import CacheControl

from .errors import FirebaseTokenError

import jose.jwt


class FirebaseToken(object):

    def __init__(self, project_id, token):
        self._project_id = project_id
        self._token = token

    @staticmethod
    def _fetch_and_cache(url):
        keys = memcache.get(url)
        if keys:
            return keys

        response = urlfetch.fetch(url)
        cache = CacheControl.parse(
            response.headers['cache-control']
        )
        if response.status_code / 400:
            logging.error("Could not fetch {}".format(url))
            logging.error("Response: {} {}".format(response.status_code, response.content))
            raise FirebaseTokenError("Cound not fetch {}".format(url))
        response = json.loads(response.content)

        memcache.set(url, response, cache.max_age)

        return response

    def validate(self):
        try:
            headers = jose.jwt.get_unverified_header(self._token)
        except JWTError as ex:
            raise FirebaseTokenError(ex)

        token_kid = headers.get('kid')

        keys = self._fetch_and_cache('https://www.googleapis.com/robot/v1/metadata/x509/securetoken@system.gserviceaccount.com')

        try:
            return jose.jwt.decode(
                self._token,
                keys.get(token_kid, ''),
                algorithms='RS256',
                audience=self._project_id,
                issuer='https://securetoken.google.com/{}'.format(
                    self._project_id,
                ),
                options={
                    'verify_sub': False,
                },
            )
        except JWTError as ex:
            raise FirebaseTokenError(ex)

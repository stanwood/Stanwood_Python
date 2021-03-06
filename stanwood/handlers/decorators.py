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
import functools
import logging
import time

from google.appengine.api import memcache
import webob.exc


def cache_control(
    max_age=None,
    s_max_age=None,
    status=frozenset((
        200,
        203,
        300,
        301,
        302,
        307,
        410,
    )),
):
    """Customize HTTP Cache-Control Header Value"""

    def decorator(f):

        @functools.wraps(f)
        def wrapper(self, *args, **kwargs):

            f(self, *args, **kwargs)

            if self.response.status_code in status:
                self.response.cache_control = 'public'
                self.response.cache_control.max_age = max_age
                self.response.cache_control.s_max_age = s_max_age

        return wrapper

    return decorator


def rate_limit(
    limit,
    seconds,
    path='',
    key=lambda self: self.request.remote_addr,
):
    """Limit number of requests"""

    def decorator(f):

        @functools.wraps(f)
        def wrapper(self, *args, **kwargs):

            timestamp = long(time.time())
            timestamp = timestamp - timestamp % seconds

            rate = memcache.incr(
                '{timestamp}|{key}|{path}'.format(
                    key=key(self),
                    path=path,
                    timestamp=timestamp,
                ),
                initial_value=0,
            )

            if rate > limit:
                raise webob.exc.HTTPTooManyRequests()

            f(self, *args, **kwargs)

        return wrapper

    return decorator


def schema(schema):
    """Validate Request's Payload with provided JSON Schema"""

    import jsonschema

    def decorator(f):

        @functools.wraps(f)
        def wrapper(self, *args, **kwargs):

            if f.__name__ == 'get':
                data = self.request.GET.mixed()
            else:
                try:
                    data = self.request.json
                except ValueError as e:
                    raise jsonschema.ValidationError(e.message)

            jsonschema.validate(data, schema)

            f(self, *args, **kwargs)

        return wrapper

    return decorator


def token_required(token):

    def wrap(func):

        def func_wrapper(self, *args, **kwargs):
            auth_token = self.request.headers.get('X-Auth-Token') or self.request.get('token')

            if auth_token != token:
                logging.error('401: {}'.format(auth_token))
                return self.abort(401, 'Unauthorized')

            return func(self, *args, **kwargs)

        return func_wrapper

    return wrap

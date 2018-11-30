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
import abc
import base64
import json
import logging
import os
import time

from google.appengine.api import urlfetch
import jose.jwt
import webapp2
import webob.exc


class MockHandler(webapp2.RequestHandler):
    """
    Generic Mock Handler that serves files from GitHub or current GAE instance.
    """

    __metaclass__ = abc.ABCMeta

    @abc.abstractproperty
    def GITHUB_APP_ID(self):
        pass

    @abc.abstractproperty
    def GITHUB_APP_KEY(self):
        pass

    @abc.abstractproperty
    def GITHUB_APP_INST(self):
        pass

    @abc.abstractproperty
    def REPO(self):
        pass

    def get(self, path):

        if path.startswith('develop/'):
            branch, path = path.split('/', 1)
        elif path.startswith('feature/'):
            branch, feature, path = path.split('/', 2)
            branch = '{}/{}'.format(branch, feature)
        else:
            branch = None

        if branch:
            response = self._fetch(
                'https://api.github.com/repos/{repo}/contents/mocks/{path}?ref={branch}'.format(
                    branch=branch,
                    path=path,
                    repo=self.REPO,
                ),
            )

            try:
                response = base64.b64decode(response['content'])
            except KeyError as e:
                raise webob.exc.HTTPNotFound()
        else:
            response = os.path.join('mocks', path)

            try:
                response = open(response)
                response = response.read()
            except IOError as e:
                raise webob.exc.HTTPNotFound()

        self.response.body = response

        # TODO Content-Type?

    @webapp2.cached_property
    def _token(self):

        now = long(time.time())

        token = jose.jwt.encode(
            {
                'iat': now,
                'exp': now + 10 * 60,
                'iss': self.GITHUB_APP_ID,
            },
            self.GITHUB_APP_KEY,
            algorithm='RS256',
        )

        response = urlfetch.fetch(
            'https://api.github.com/installations/{}/access_tokens'.format(
                self.GITHUB_APP_INST,
            ),
            method='POST',
            headers={
                'Accept': 'application/vnd.github.machine-man-preview+json',
                'Authorization': 'Bearer {}'.format(token),
            },
        )
        response = json.loads(response.content)

        return response['token']

    def _fetch(self, *args, **kwargs):

        try:
            headers = kwargs['headers']
        except KeyError:
            headers = kwargs['headers'] = {}
        finally:
            headers.update({
                'Accept': 'application/vnd.github.machine-man-preview+json',
                'Authorization': 'token {}'.format(self._token),
            })

        response = urlfetch.fetch(*args, **kwargs)
        response = json.loads(response.content)

        if 'errors' in response:
            logging.error(response)
            raise webob.exc.HTTPInternalServerError()

        return response

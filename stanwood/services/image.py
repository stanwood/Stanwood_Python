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
import urllib

from google.appengine.ext import ndb


class ImageServiceError(Exception):
    pass


class ImageService(object):
    """
    Client for Stanwood Image Service.
    """

    HOST = 'https://stanwood-image-service.appspot.com'
    DEADLINE = 15

    def __init__(self, namespace, token):

        self.__namespace = namespace
        self.__token = token

    @ndb.tasklet
    def __call__(self, path, *args, **kwargs):

        try:
            headers = kwargs['headers']
        except KeyError:
            headers = kwargs['headers'] = {}
        finally:
            headers.update({
                'X-Auth-Token': self.__token,
            })

        if kwargs.get('method', 'GET') == 'GET' and 'payload' in kwargs:
            # path += '?' + urllib.urlencode(kwargs.pop('payload'))
            path += '?' + '&'.join(
                '{}={}'.format(
                    key,
                    value,
                )
                for key, value in kwargs.pop('payload').iteritems()
            )

        response = yield ndb.get_context().urlfetch(
            '{}/{}{}'.format(
                self.HOST,
                self.__namespace,
                path,
            ),
            deadline=self.DEADLINE,
            **kwargs
        )

        if response.status_code != 302:
            raise ImageServiceError(response.content)

        raise ndb.Return(response)

    def Image(self, url):
        return _Image(self, url)


class _Image(object):
    """
    Image (URL) representation with available transformation methods.
    """

    def __init__(self, service, url):

        self.__service = service
        self.__url = url

    def crop(self, top, left, right, bottom):
        return self.transform(
            crop='{top},{left},{right},{bottom}'.format(
                top=top,
                left=left,
                right=right,
                bottom=bottom,
            ),
        )

    def resize(self, width):
        return self.transform(
            width=width,
        )

    @ndb.tasklet
    def transform(self, **kwargs):

        kwargs.update({
            'url': urllib.quote(self.__url, safe=''),
        })

        response = yield self.__service(
            '/image',
            follow_redirects=False,
            method='GET',
            payload=kwargs,
        )

        raise ndb.Return(response.headers['location'])

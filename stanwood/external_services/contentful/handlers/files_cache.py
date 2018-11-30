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
import os

from google.appengine.api import memcache
from google.appengine.api import urlfetch
from google.appengine.ext import ndb

from stanwood.external_services.contentful.handlers.base import CustomBaseHandler
from stanwood.external_services.contentful.models.contentful_file import ContentfulFile


class FilesCacheBaseHandler(CustomBaseHandler):

    @property
    def memcache_key(self):
        return self.request.path_qs

    @property
    def folder(self):
        return self.request.route_kwargs['source_host']

    @property
    def CONTENTFUL_URL(self):
        return 'https://{}'.format(self.request.route_kwargs['source_host'])

    @property
    def file_path(self):
        return self.request.route_kwargs.get('file_path')

    @property
    def file_path_with_parameters(self):
        if self.request.query_string:
            file_path_with_parameters = u'{}?{}'.format(self.file_path, self.request.query_string)
        else:
            file_path_with_parameters = self.file_path

        return file_path_with_parameters

    @property
    def file_url(self):
        return '{}/{}'.format(self.CONTENTFUL_URL, self.file_path_with_parameters)

    def dispatch(self):
        redirect_url = memcache.get(self.memcache_key)
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.headers['Cache-Control'] = 'no-cache'
        if redirect_url:
            self.redirect(redirect_url, code=303)
        else:
            super(FilesCacheBaseHandler, self).dispatch()
            memcache.set(
                self.memcache_key,
                self.response.headers['location']
            )

    def get(self, file_path, source_host=None):
        _, file_name = os.path.split(file_path)

        contentful_file = ndb.Key(ContentfulFile, self.file_url).get()

        if contentful_file is None:
            logging.debug("Image not cached")
            response = urlfetch.fetch(self.file_url, deadline=60)
            blob = self.store(
                file_name=self.file_path_with_parameters+u'/'+file_name,
                file_data=response.content,
                content_type=response.headers.get('content-type', 'application/octet-stream')
            )
            blob.make_public()

            contentful_file = ContentfulFile(
                id=self.file_url,
                public_url=blob.public_url,
                name=blob.name,
                memcache_key=self.memcache_key
            )
            contentful_file.put()

        self.redirect(contentful_file.public_url.encode('utf-8'), code=303)

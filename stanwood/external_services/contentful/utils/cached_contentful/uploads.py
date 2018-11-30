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
import mimetypes
import uuid

from urlparse import urlparse
from os.path import splitext, basename


class Image(object):
    def __init__(self, bucket):
        self.bucket = bucket

    @staticmethod
    def get_details(image_url):
        disassembled = urlparse(image_url)
        filename, extension = splitext(basename(disassembled.path))
        content_type = mimetypes.guess_type(image_url)[0]
        filename += '-' + str(uuid.uuid4())
        return filename, extension, content_type

    @staticmethod
    def normalize_url(url):
        """Adds htpp protocol"""
        return 'http:' + url

    def upload_blob(self, filename, extension, content, content_type):
        blob = self.bucket.blob(filename + extension)
        blob.upload_from_string(content, content_type)
        return blob.public_url

    def upload(self, data):
        if not isinstance(data, list):
            data = [data]

        for image in data:
            image_url = self.normalize_url(image['fields']['file']['url'])
            fetched_image = urlfetch.fetch(image_url, deadline=60)
            filename, extension, content_type = self.get_details(image_url)
            blob_url = self.upload_blob(
                filename,
                extension,
                fetched_image.content,
                content_type
            )
            image['fields']['file']['url'] = blob_url
        return data if len(data) > 1 else data[0]

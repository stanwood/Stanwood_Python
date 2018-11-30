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

import google.cloud.storage
import webapp2

from google.appengine.api.app_identity import app_identity
from retrying import retry


class CloudStorageMixin(object):
    __metaclass__ = abc.ABCMeta

    @property
    def storage(self):
        # Create GCS client for each request.
        # It's a workaround for NotAllowed exception when calling app_identity methods.
        return google.cloud.storage.Client()

    @abc.abstractproperty
    def folder(self):
        pass

    @webapp2.cached_property
    def bucket(self):
        return self.storage.bucket(
            app_identity.get_default_gcs_bucket_name()
        )

    @retry(stop_max_attempt_number=3)
    def store(
        self, file_name, file_data,
        content_type='application/octet-stream',
        directory=None, metadata=None,
    ):
        blob_name = u'{}/{}'.format(directory or self.folder, file_name)
        blob_name = blob_name.encode('utf-8')
        blob = self.bucket.blob(blob_name)

        if metadata:
            blob.metadata = metadata

        blob.upload_from_string(file_data, content_type)

        return blob

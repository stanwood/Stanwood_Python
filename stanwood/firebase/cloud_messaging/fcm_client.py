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

from google.appengine.api import urlfetch, app_identity


class FcmClientError(Exception):
    pass


class FcmClient(object):

    def __init__(self, project_id):
        self._project_id = project_id

    @property
    def access_token(self):
        return app_identity.get_access_token(
            scopes=[
                'https://www.googleapis.com/auth/firebase.messaging'
            ]
        )[0]

    def push(self, payload):
        payload = json.dumps(payload, indent=2)
        logging.debug(payload)
        url = 'https://fcm.googleapis.com/v1/projects/{}/messages:send'.format(self._project_id)
        logging.debug(u'POST {} \n {}'.format(url, json.dumps(payload, indent=2)))
        result = urlfetch.fetch(
            url=url,
            method='POST',
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'Bearer {}'.format(self.access_token)
            },
            payload=payload
        )

        if result.status_code / 400:
            raise FcmClientError('Failed to send push: {} {}'.format(result.status_code, result.content))

        return json.loads(result.content)

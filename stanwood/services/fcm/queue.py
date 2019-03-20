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
import os

from google.appengine.api import (
    app_identity,
    taskqueue,
)
from google.appengine.ext import ndb

import webapp2


class FcmQueueHandler(webapp2.RequestHandler):

    LIMIT = 4

    @property
    def access_token(self):
        return app_identity.get_access_token(
            scopes=[
                'https://www.googleapis.com/auth/firebase.messaging'
            ]
        )[0]

    @ndb.toplevel
    def post(self):

        request = self.request.json

        logging.info(request)

        project = request.pop('PROJECT')

        response = yield ndb.get_context().urlfetch(
            'https://fcm.googleapis.com/v1/projects/{}/messages:send'.format(
                project,
            ),
            json.dumps(request),
            'POST',
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'Bearer {}'.format(self.access_token)
            },
        )

        logging.debug(response.content)

        if response.status_code / 400:
            self.abort(response.status_code)


app = webapp2.WSGIApplication(
    (
        webapp2.Route(r'/_ah/queue/fcm', FcmQueueHandler),
    ),
)

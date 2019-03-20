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


class EmailQueueHandler(webapp2.RequestHandler):

    @ndb.toplevel
    def post(self):

        request = self.request.json

        if 'template' in request:
            response = yield ndb.get_context().urlfetch(
                'https://mandrillapp.com/api/1.0/messages/send-template.json',
                json.dumps({
                    'key': os.environ.get('MANDRILL_KEY'),
                    'template_content': [],
                    'template_name': request['template'],
                    'message': {
                        'global_merge_vars': [
                            {
                                'name': key,
                                'content': value
                            }
                            for key, value in request['kwargs'].iteritems()
                        ],
                        'to': [
                            {
                                'email': request['to'],
                                'type': 'to',
                            },
                        ],
                    },
                }),
                'POST',
                headers={
                    'Content-Type': 'application/json',
                },
            )

            if response.status_code != 200:
                logging.error(response.content)
                self.abort(response.status_code)


app = webapp2.WSGIApplication(
    (
        webapp2.Route(r'/_ah/queue/email', EmailQueueHandler),
    ),
)

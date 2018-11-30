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
import os

from google.appengine.api import taskqueue
from google.appengine.ext import ndb

import webapp2

from stanwood.external_services.slack.slack import Slack


class SlackQueueHandler(webapp2.RequestHandler):

    LIMIT = 4

    @ndb.toplevel
    @ndb.transactional
    @ndb.tasklet
    def post(self):

        queue = os.environ.get('SLACK_QUEUE', 'default')
        queue = taskqueue.Queue(queue)

        messages = self.request.json

        if isinstance(messages, dict):

            slack = Slack(
                os.environ.get('SLACK_BOT_TOKEN', None),
                os.environ.get('SLACK_APP_TOKEN', None),
            )
            thread = messages.pop('_thread', [])
            response = slack.post_message(messages)

            if thread:
                for message in thread:
                    message['thread_ts'] = response['ts']

                yield queue.add_async(
                    taskqueue.Task(
                        payload=json.dumps(thread),
                    ),
                    transactional=True,
                )

            raise ndb.Return()

        tasks = [
            taskqueue.Task(
                payload=json.dumps(message),
            )
            for message in messages[:self.LIMIT]
        ]

        messages = messages[self.LIMIT:]

        if messages:
            tasks.append(
                taskqueue.Task(
                    payload=json.dumps(messages),
                    url='/_ah/queue/slack',
                )
            )

        yield queue.add_async(
            tasks,
            transactional=True,
        )


app = webapp2.WSGIApplication(
    (
        webapp2.Route(r'/_ah/queue/slack', SlackQueueHandler),
    ),
)

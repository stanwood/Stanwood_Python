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
"""
In order to use this, please add to you ``app.yaml`` following lines::

    includes:
    - lib/stanwood/stanwood/services/slack/include.yaml

    env_variables:
      SLACK_BOT_TOKEN: 'BOT-token'
      SLACK_APP_TOKEN: 'APP-token'

By default messages will be sent to ``default`` queue. Optionally add::

    env_variables:
      SLACK_QUEUE: 'slack'

and configure it in ``queue.yaml`` accordingly::

    queue:
    - name: slack
      mode: push
      rate: 1/s

Now you are ready to use ``stanwood.services.slack.send_message`` function.
"""

import json
import os

from google.appengine.api import taskqueue


def send_template(
    to,
    template,
    _transactional=False,
    **kwargs
):
    return taskqueue.add(
        payload=json.dumps({
            'to': to,
            'template': template,
            'kwargs': kwargs,
        }),
        queue_name=os.environ.get('EMAIL_QUEUE', 'default'),
        transactional=_transactional,
        url='/_ah/queue/email',
    )

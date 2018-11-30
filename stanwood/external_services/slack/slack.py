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
import unicodedata
import urllib

from google.appengine.api import urlfetch


class SlackError(Exception):
    pass


class SlackLimitRateError(SlackError):
    pass


class Slack(object):
    BASE_URL = 'https://slack.com/api/'

    def __init__(self, bot_token, app_token):
        if isinstance(bot_token, unicode):
            bot_token = bot_token.encode('ascii')
        if isinstance(app_token, unicode):
            app_token = app_token.encode('ascii')

        self.bot_token = bot_token
        self.app_token = app_token

    @staticmethod
    def _normalize_unicode(text):
        return str(unicodedata.normalize('NFKD', text).encode('ascii', 'ignore'))

    @classmethod
    def _normalize_values(cls, input):

        if isinstance(input, unicode):
            return cls._normalize_unicode(input)
        elif isinstance(input, list):
            return [cls._normalize_values(v) for v in input]
        elif isinstance(input, dict):
            return dict(
                [
                    (
                        str(key),
                        cls._normalize_values(value),
                    )
                    for key, value in input.iteritems()
                    ]
            )
        else:
            return input

    def request(self, method, message=None):
        if message is None:
            message = {}
        if message.get('as_user'):
            message['token'] = self.app_token
        else:
            message['token'] = self.bot_token

        message = self._normalize_values(message)

        logging.debug('POST {} {}'.format(method, message))

        # response = requests.post(
        #     url=self.BASE_URL + method,
        #     params=message
        # )

        response = urlfetch.fetch(
            url=self.BASE_URL + method,
            payload=urllib.urlencode(message),
            method='POST'
        )
        logging.debug('Response: {}'.format(response.content))
        if response.status_code / 400:
            raise SlackError(response.content)

        content = json.loads(response.content)
        if content['ok'] is False:
            if content['error'] == 'ratelimited':
                raise SlackLimitRateError(response.content)
            else:
                raise SlackError(content['error'])
        return json.loads(response.content)

    def post_message(self, message):
        return self.request('chat.postMessage', message)

    def update_message(self, message):
        return self.request('chat.update', message)

    def delete_message(self, message):
        return self.request('chat.delete', message)

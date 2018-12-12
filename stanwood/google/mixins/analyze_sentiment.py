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

import requests
import webapp2
from google.appengine.api import app_identity


class GoogleAPI(object):

    SCOPES = (
        'https://www.googleapis.com/auth/cloud-language',
        'https://www.googleapis.com/auth/cloud-platform',
    )

    @webapp2.cached_property
    def google_auth_token(self):
        auth_token, _ = app_identity.get_access_token(
            self.SCOPES
        )
        return auth_token

    def analyze_sentiment(self, text):
        """
        API Reference:
            https://cloud.google.com/natural-language/docs/reference/rest/v1beta2/documents/analyzeSentiment
        """
        url = 'https://language.googleapis.com/v1beta2/documents:analyzeSentiment'

        response = requests.post(
            url,
            json={
                'document': {
                  'type': 'PLAIN_TEXT',
                  'language': 'en',
                  'content': text,
                }
            },
            headers={'Authorization': 'Bearer {}'.format(self.google_auth_token)}
        )

        if response.status_code / 400:
            logging.error('Google analyzeSentiment is not responding. Response body:\n' + response.content)
            raise webapp2.exc.HTTPBadGateway()

        return response.json()


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

import webapp2

from stanwood.handlers.mixins.cors import CorsMixin
from stanwood.firebase.decorators.firebase_token_required import firebase_token_required


class ContentfulAccessTokenBaseHandler(CorsMixin, webapp2.RequestHandler):
    CONTENTFUL_MANAGEMENT_TOKEN = None

    @firebase_token_required({})
    def get(self):
        self.response.content_type = 'application/json'
        self.response.write(
            json.dumps(
                {
                    'accessToken': self.CONTENTFUL_MANAGEMENT_TOKEN
                }
            )
        )

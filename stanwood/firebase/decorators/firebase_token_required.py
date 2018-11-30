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
import os

import json
import logging
import functools

from stanwood.firebase.token.errors import FirebaseTokenError
from stanwood.firebase.token.firebase_token import FirebaseToken


def firebase_token_required(claims):
    """
    Verify firebase token. It requires os.environ['FIREBASE_PROJECT'] which should contain Firebase project name.
    :param claims list of firebase claims to check
    """

    def decorator(f):

        @functools.wraps(f)
        def check_token(self, *args, **kwargs):

            if self.request.method != 'OPTIONS':
                token = self.request.headers.get('X-Auth-Token')
                token = FirebaseToken(os.environ['FIREBASE_PROJECT'], token)

                try:
                    decoded_token = token.validate()
                    logging.debug(json.dumps(decoded_token, indent=2))
                except FirebaseTokenError as token_error:
                    logging.exception(token_error)
                    return self.abort(401, token_error)

                if claims:
                    for claim, value in claims.iteritems():
                        try:
                            if decoded_token[claim] != value:
                                logging.error('Claim value `{}` not equal expected`{}`'.format(claim, value))
                                return self.abort(401, 'Missing claim {}'.format(claim))
                        except KeyError as key_error:
                            logging.error('User misess claim `{}`'.format(claim))
                            return self.abort(401, 'Missing claim {}'.format(claim))

            return f(self, *args, **kwargs)

        return check_token

    return decorator

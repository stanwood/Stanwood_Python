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
import random
import string

from google.appengine.ext import ndb


class AuthorizationStateError(Exception):
    pass


class AuthorizationState(ndb.Model):
    state = ndb.StringProperty()
    user_id = ndb.StringProperty()

    @classmethod
    def save_state(cls, user_id=None):
        state = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(64))
        cls(state=state, user_id=user_id).put()
        return state

    @classmethod
    def validate_state(cls, state):
        stored_state = cls.query(cls.state == state).get()
        if stored_state:
            user_id = stored_state.user_id
            logging.debug('State correct. User id {}'.format(user_id))
            stored_state.key.delete()
            return user_id
        else:
            raise AuthorizationStateError("Invalid state {}".format('state'))

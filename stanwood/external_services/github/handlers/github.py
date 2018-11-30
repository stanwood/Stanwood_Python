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
import abc

import rauth
import webapp2

from stanwood.external_services.github.models.authorization_state import AuthorizationState


class OauthHandler(webapp2.RequestHandler):

    __metaclass__ = abc.ABCMeta

    CLIENT_ID = ''
    CLIENT_SECRET = ''

    @property
    def oauth(self):
        return rauth.OAuth2Service(
            client_id=self.CLIENT_ID,
            client_secret=self.CLIENT_SECRET,
            name='github',
            access_token_url='https://github.com/login/oauth/access_token',
            authorize_url='https://github.com/login/oauth/authorize',
        )


class GithubAuthorizeHandler(OauthHandler):

    @property
    def user_id(self):
        return self.request.get('user_id')

    def get(self):
        state = AuthorizationState.save_state(self.user_id)
        self.redirect(
            self.oauth.get_authorize_url(
                scope='repo',
                state=state,
                redirect_uri='https://{}{}'.format(
                    self.request.host,
                    webapp2.uri_for('github-callback')
                )
            )
        )


class GithubCallbackHandler(OauthHandler):

    @abc.abstractmethod
    def store_token(self, user_id, access_token):
        pass

    @property
    def code(self):
        return self.request.get('code')

    @property
    def state(self):
        return self.request.get('state')

    def get(self):
        user_id = AuthorizationState.validate_state(self.state)

        access_token = self.oauth.get_access_token(
            params={
                'code': self.code
            },
            method='POST'
        )

        self.store_token(user_id, access_token)

        self.response.write('Ok, this looks good. Got your github credentials.')


class GithubTestCallbackHandler(GithubCallbackHandler):
    """ Just for unit testing"""
    def store_token(self, user_id, access_token):
        pass

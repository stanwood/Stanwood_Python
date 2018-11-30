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
import mock
import pytest

from stanwood.external_services.github.models.authorization_state import AuthorizationState


@pytest.fixture
def oauth(testbed):
    with mock.patch('stanwood.external_services.github.handlers.github.OauthHandler.oauth', new_callable=mock.PropertyMock) as oauth_mock:
        yield oauth_mock


@pytest.fixture
def store_token(testbed):
    with mock.patch('stanwood.external_services.github.handlers.github.GithubTestCallbackHandler.store_token') as store_token_mock:
        yield store_token_mock


def test_authorize_link(app):

    response = app.get(
        '/github/authorize',
        params={
            'user_id': 'user-1'
        },
        status=302
    )

    state = AuthorizationState.query().get()

    assert state
    assert state.user_id == 'user-1'
    assert 'https://github.com/login/oauth/authorize' in response.headers['location']
    assert 'state={}'.format(state.state) in response.headers['location']


def test_callback(app, oauth, store_token):

    AuthorizationState(state='our-state', user_id='user-1').put()
    oauth.return_value.get_access_token.return_value = 'github-token'

    app.get(
        '/github/callback',
        params={
            'code': 'github-code',
            'state': 'our-state'
        }
    )

    store_token.assert_called_with('user-1', 'github-token')

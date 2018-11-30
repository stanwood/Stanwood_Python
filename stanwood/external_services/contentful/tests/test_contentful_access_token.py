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

import mock
import pytest


@pytest.fixture
def config(testbed):
    with mock.patch('stanwood.external_services.contentful.handlers.contentful_access_token.ContentfulAccessTokenBaseHandler.CONTENTFUL_MANAGEMENT_TOKEN', new_callable=mock.PropertyMock) as config_mock:
        config_mock.return_value = os.environ['CONTENTFUL_MANAGEMENT_TOKEN']
        yield config_mock


def test_authorization(app):
    app.get('/manage/contentful/access_token', status=401)


def test_get_access_token(app, config, verify_id_token):
    response = app.get('/manage/contentful/access_token')
    assert response.json == {
        'accessToken': 'contentful-management-token'
    }

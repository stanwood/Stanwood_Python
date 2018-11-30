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
# coding: utf-8
import os

import mock
import pytest


@pytest.fixture
def fetch(testbed):
    with mock.patch('stanwood.external_services.contentful.handlers.contentful_management_proxy.urlfetch.fetch') as fetch_mock:
        yield fetch_mock


@pytest.fixture
def config_contentful_management_token(testbed):
    with mock.patch('stanwood.external_services.contentful.handlers.contentful_management_proxy.ContentfulManagementProxyBaseHandler.CONTENTFUL_MANAGEMENT_TOKEN', new_callable=mock.PropertyMock) as contentful_management_token_mock:
        contentful_management_token_mock.return_value = os.environ['CONTENTFUL_MANAGEMENT_TOKEN']
        yield contentful_management_token_mock

@pytest.fixture
def config_contentful_space(testbed):
    with mock.patch('stanwood.external_services.contentful.handlers.contentful_management_proxy.ContentfulManagementProxyBaseHandler.CONTENTFUL_SPACE', new_callable=mock.PropertyMock) as contentful_space_mock:
        contentful_space_mock.return_value = os.environ['CONTENTFUL_SPACE']
        yield contentful_space_mock


def test_proxy_request(
        app,
        fetch,
        verify_id_token,
        config_contentful_management_token,
        config_contentful_space,
    ):

    fetch.return_value = mock.Mock(
        content='{"foo":"bar"}',
        headers={
            'content-type': 'application/json'
        },
        status_code=200
    )

    response = app.post(
        '/manage/contentful/spaces/in1ws0j2cnhw/entries',
        headers={
            'Content-type': 'application/json'
        },
        params='{"foo":"bar"}'
    )

    fetch.assert_called_with(
        u'https://api.contentful.com/spaces/in1ws0j2cnhw/entries?',
        headers={
            'Host': 'localhost:80',
            'Content-Type': 'application/json',
            'Content-Length': '13',
            'Authorization': 'Bearer contentful-management-token'
        },
        method='POST',
        payload='{"foo":"bar"}',
        deadline=60
    )

    assert response.body == '{"foo":"bar"}'


def test_add_space_if_missing(
        app,
        fetch,
        verify_id_token,
        config_contentful_management_token,
        config_contentful_space,
):
    fetch.return_value = mock.Mock(
        content='abc',
        headers={
            'content-type': 'text'
        },
        status_code=200
    )

    response = app.get(
        '/manage/contentful/entries?content_type=article&limit=10',
        headers={
            'Authorization': 'Bearer contentful-token'
        }
    )

    fetch.assert_called_with(
        'https://api.contentful.com/spaces/contentful-space/entries?content_type=article&limit=10',
        headers={
            'Host': 'localhost:80',
            'Authorization': 'Bearer contentful-management-token'
        },
        method='GET',
        payload='',
        deadline=60
    )


def test_cors(app):

    response = app.options('/manage/contentful/spaces/')

    print response.headers.keys()


def test_check_token(app):

    app.get('/manage/contentful/foo', status=401)
    app.post('/manage/contentful/foo', status=401)
    app.put('/manage/contentful/foo', status=401)
    app.delete('/manage/contentful/foo', status=401)

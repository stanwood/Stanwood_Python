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


@pytest.fixture
def fetch(testbed):
    with mock.patch('stanwood.handlers.proxy.urlfetch.fetch') as fetch_mock:
        yield fetch_mock


def test_proxy_request(app, fetch):

    fetch.return_value = mock.Mock(
        status_code=200,
        content='bar',
        headers={
            'Content-Type': 'text/plain',
        },
    )

    response = app.get('/proxy/foo/1', params={'arg': 'val'}, headers={'token': 'foo'}, status=200)
    assert response.body == 'bar'
    fetch.assert_called_with(
        '/foo/1?arg=val',
        deadline=60,
        headers=mock.ANY,
        method='GET',
        payload=''
    )
    headers = dict(fetch.mock_calls[0][2]['headers'].items())
    assert headers['Token'] == 'foo'

    response = app.post('/proxy/foo/1', params={'arg': 'val'}, headers={'token': 'foo'}, status=200)
    assert response.body == 'bar'
    fetch.assert_called_with(
        '/foo/1',
        deadline=60,
        headers=mock.ANY,
        method='POST',
        payload='arg=val'
    )
    headers = dict(fetch.mock_calls[0][2]['headers'].items())
    assert headers['Token'] == 'foo'

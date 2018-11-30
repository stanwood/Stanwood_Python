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


def test_redirect_to_download_link(app, contentful, response):

    contentful.return_value.asset.return_value = response(
        {
            'fields':
                {
                    'file': {
                        'url': 'http://foo.bar'
                    }
                }
        }

    )

    response = app.get('/contentful/download/foo', status=302)

    assert response.headers['location'] == 'http://foo.bar'


def test_cors_added_to_not_found_response(app, contentful):

    contentful.return_value.asset.return_value = mock.Mock(
        status_code=404,
        content="{}"
    )

    response = app.get('/contentful/download/foo', expect_errors=True)

    assert 'Access-Control-Allow-Origin' in response.headers
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
import pytest


@pytest.fixture
def contentful(testbed, response, contentful):
        contentful.return_value.entries.return_value = response(
            {
                'foo': 'bar'
            }
        )
        yield contentful


def test_get_all_entries(app, contentful):
    response = app.get(
        '/contentful/entries'
    )
    assert response.json == {
        'foo': 'bar'
    }


def test_public_caching_headers(app, contentful):
    response = app.get(
        '/contentful/entries'
    )
    assert response.headers['Cache-Control'] == 'max-age=60, public, s-maxage=60'


def test_select_parameter(app, contentful):
    response = app.get(
        '/contentful/entries?select=fields.title'
    )


def test_root_endpoint(app, contentful):
    app.get('/contentful/')
    contentful.return_value.root_endpoint.assert_called()

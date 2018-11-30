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

import mock
import pytest

from google.appengine.api import memcache

from stanwood.external_services.contentful.utils.cached_contentful import cached_contentful


@pytest.fixture
def http_get(testbed):
    with mock.patch('stanwood.external_services.contentful.utils.cached_contentful.cached_contentful.contentful.Client._http_get') as http_get_mock:
        yield http_get_mock


@pytest.fixture
def contentful(testbed):
    yield cached_contentful.Client(
        'space',
        'token',
        base_url='https://my-api-dev.appspot.com',
        content_type_cache=False  # avoid extra http call which messes with mocking
    )


def test_get_entries(http_get, contentful, response):
    test_response = {'foo': 'bar', 'bar': 'foo'}
    http_get.return_value = response(test_response)
    assert contentful.entries().content == json.dumps(test_response)
    assert memcache.get(u'contentful:space:/entries?{}') == json.dumps(test_response)

    contentful.entries()
    http_get.assert_called_once()


def test_entry_by_id(http_get, contentful, response):
    http_get.return_value = response({'foo': 'bar'})
    assert contentful.entry('1').content == json.dumps({'foo': 'bar'})
    assert memcache.get(u'contentful:space:/entries?{"sys.id": "1"}') == json.dumps({'foo': 'bar'})
    contentful.entry('1')
    http_get.assert_called_once()


def test_replace_images_urls_in_includes(http_get, contentful, response):
    http_get.return_value = response(
        {
            'includes': {
                'Asset': [
                    {
                        'sys':{
                            'id': 'asset-1'
                        },
                        'fields': {
                            'file': {
                                'url': '//images.contentful.com/in1ws0j2cnhw/106HCLFiMYoUk6mYqK44ye/'
                                       'c9ead673c8996d23511e0f57225402ea/asset_11158.jpg'
                            }
                        }
                    }
                ]
            }

        }

    )
    entries = contentful.entries()
    assert json.loads(entries.content)['includes']['Asset'][0]['fields']['file']['url'] == (
        'https://my-api-dev.appspot.com/contentful/files_cache/images.contentful.com/'
        'in1ws0j2cnhw/106HCLFiMYoUk6mYqK44ye/c9ead673c8996d23511e0f57225402ea/asset_11158.jpg'
    )


def test_replace_images_urls_in_items(http_get, contentful, response):
    http_get.return_value = response(
        {
            'items': [
                {
                    'sys': {
                        'type': 'Asset'
                    },
                    'fields': {
                        'file': {
                            'url': '//images.ctfassets.net/in1ws0j2cnhw/3VuS2MHXxYs042wYgsAiAM/'
                                   '1f188583c323a7f52358643e1a2a2e62/Screen_Shot.png'
                        }
                    }
                }
            ]
        }
    )
    entries = contentful.assets()
    assert json.loads(entries.content)['items'][0]['fields']['file']['url'] == (
        'https://my-api-dev.appspot.com/contentful/files_cache/images.ctfassets.net/'
        'in1ws0j2cnhw/3VuS2MHXxYs042wYgsAiAM/1f188583c323a7f52358643e1a2a2e62/Screen_Shot.png'
    )


def test_cache_when_contentful_adds_sys_field_to_select(http_get, contentful, response):

    http_get.return_value = response(
        {'foo': 'bar'}
    )

    contentful.entries(
        {u'foo130': u'', u'limit': u'10', u'select': u'fields.title', u'content_type': u'article'}
    )

    memcache_key = (u'contentful:space:/entries?{"content_type": "article", "limit": "10", '
                    u'"select": ["fields.title", "sys"], "foo130": ""}')

    assert memcache.get(memcache_key) == json.dumps({'foo': 'bar'})

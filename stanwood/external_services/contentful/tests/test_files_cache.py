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
from google.appengine.api import memcache
from google.appengine.ext import ndb

from stanwood.external_services.contentful.models.contentful_file import ContentfulFile


@pytest.fixture
def fetch(testbed):
    with mock.patch('stanwood.external_services.contentful.handlers.files_cache.urlfetch.fetch') as fetch_mock:
        yield fetch_mock


@pytest.mark.parametrize(
    'file_path',
    (
            'in1ws0j2cnhw/106HCLFiMYoUk6mYqK44ye/c9ead673c8996d23511e0f57225402ea/asset_11158.jpg?w=200',
            'in1ws0j2cnhw/106HCLFiMYoUk6mYqK44ye/c9ead673c8996d23511e0f57225402ea/asset_11158.jpg'
    )
)
@pytest.mark.parametrize(
    'url',
    (
        ('/contentful/files_cache/images.contentful.com/', 'https://images.contentful.com'),
    ),
)
def test_upload_image(app, fetch, bucket, file_path, url):

    fetch.return_value = mock.MagicMock(
        content='image data',
        headers={'content-type': 'image/jpg'}
    )
    blob = mock.MagicMock()
    blob.public_url = 'http://foo.com/image.png'
    blob.name = 'image.png'
    bucket.return_value.blob.return_value = blob

    response = app.get(
        url[0]+file_path,
        status=303
    )

    file_url = '{}/{}'.format(url[1], file_path)
    contentful_file = ndb.Key(ContentfulFile, file_url).get()

    assert contentful_file
    assert contentful_file.public_url == response.headers['location']
    print response.headers['location']

    blob.make_public.assert_called()
    blob.upload_from_string.assert_called_with(
        'image data',
        'image/jpg'
    )


@pytest.fixture
def key(testbed):
    with mock.patch('stanwood.external_services.contentful.handlers.files_cache.ndb.Key') as key_mock:
        yield key_mock


@pytest.mark.parametrize(
    'url',
    (
        '/contentful/files_cache/images.contentful.com/',
    )
)
def test_redirect_url_cached(app, url, key):

    file_path = 'foo/bar.jpg'

    key.return_value.get.return_value = ContentfulFile(
        id=file_path,
        public_url='http://foo.bar'
    )

    assert memcache.get(file_path) is None
    app.get(url+file_path, status=303)
    assert memcache.get(url+file_path) == 'http://foo.bar'
    app.get(url + file_path, status=303)

    key.return_value.get.assert_called_once()

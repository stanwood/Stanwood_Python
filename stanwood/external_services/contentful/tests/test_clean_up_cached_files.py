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
import datetime

import mock
import pytest

from stanwood.external_services.contentful.models.contentful_file import ContentfulFile


@pytest.fixture
def memcache(testbed):
    with mock.patch('stanwood.external_services.contentful.handlers.clean_up_cached_files.memcache') as memcache_mock:
        yield memcache_mock


def test_clean_up(app, bucket, memcache):
    blob = mock.MagicMock()
    bucket.return_value.blob.return_value = blob

    ContentfulFile(
        name='foo/bar',
        created=datetime.datetime.utcnow() - datetime.timedelta(days=31),
        memcache_key='key'
    ).put()

    app.get('/tasks/clean-up')

    assert ContentfulFile.query().get() is None
    blob.delete.assert_called()
    memcache.delete.assert_called_with('key')

    # not old enough
    blob.reset_mock()
    memcache.reset_mock()
    ContentfulFile(
        name='foo/bar',
        created=datetime.datetime.utcnow() - datetime.timedelta(days=29),
        memcache_key='key'
    ).put()

    app.get('/tasks/clean-up')

    assert ContentfulFile.query().get()
    blob.delete.assert_not_called()
    memcache.delete.assert_not_called()

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
import os

import mock
import pytest

from dev_appserver import fix_sys_path
fix_sys_path()

import appengine_config

import webtest

from stanwood.pytest.appengine import freezegun_patch


@pytest.fixture
def testbed():

    from google.appengine.ext import testbed

    tb = testbed.Testbed()
    tb.activate()

    tb.setup_env(
        application_id='my-api-dev',
        google_cloud_project='my-api-dev',
        overwrite=True,
        CONTENTFUL_SPACE='contentful-space',
        CONTENTFUL_TOKEN='contentful-token',
        CONTENTFUL_MANAGEMENT_TOKEN='contentful-management-token',
        FIREBASE_PROJECT='wfv-cms-develop',
        FIREBASE_CLOUD_FUNCTIONS_TOKEN='firebase-cloud-functions-token',
    )

    tb.init_app_identity_stub()
    tb.init_memcache_stub()
    tb.init_urlfetch_stub()
    tb.init_app_identity_stub()
    tb.init_search_stub()
    tb.init_datastore_v3_stub()

    base_dir = os.path.abspath((os.path.dirname(__file__)))

    tb.init_taskqueue_stub(root_path=os.path.join(base_dir, '..'))
    tb.MEMCACHE_SERVICE_NAME = testbed.MEMCACHE_SERVICE_NAME
    tb.TASKQUEUE_SERVICE_NAME = testbed.TASKQUEUE_SERVICE_NAME

    yield tb

    tb.deactivate()


@pytest.fixture
def app(testbed):
    import main_app
    return webtest.TestApp(main_app.app)


@pytest.fixture
def taskqueue(testbed):
    yield testbed.get_stub(testbed.TASKQUEUE_SERVICE_NAME)


@pytest.fixture
def response(testbed):

    def get_response(json_response, status_code=200):
        response_mock = mock.MagicMock()
        response_mock.status_code = 200
        response_mock.content = json.dumps(json_response)
        return response_mock

    yield get_response


@pytest.fixture
def bucket(testbed):
    with mock.patch('stanwood.handlers.mixins.gcs.CloudStorageMixin.bucket', new_callable=mock.PropertyMock) as bucket_mock:
        yield bucket_mock


@pytest.fixture
def contentful(testbed):
    with mock.patch(
        'stanwood.external_services.contentful.handlers.mixins.contentful_mixin.ContentfulMixin.contentful',
        new_callable=mock.PropertyMock
    ) as contentful_mock:
        yield contentful_mock


@pytest.fixture
def verify_id_token(testbed):
    with mock.patch('stanwood.firebase.token.firebase_token.FirebaseToken.validate') as mock_verify_id_token:
        mock_verify_id_token.return_value = {}
        yield mock_verify_id_token

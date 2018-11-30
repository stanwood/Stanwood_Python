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


from google.appengine.ext import ndb


class FirestoreRESTClient(object):

    FIRESTORE_API_URL = 'https://firestore.googleapis.com'
    FIRESTORE_API_VERSION = 'v1beta1'

    REQUEST_TIMEOUT = 60

    def __init__(self, firebase_app, firebase_project_name, database_name='default'):
        self.firebase_app = firebase_app

        self.database_name = '({})'.format(database_name)

        self.project_path = 'projects/{}'.format(firebase_project_name)

        self.firestore_api_url = '{}/{}'.format(
            self.FIRESTORE_API_URL,
            self.FIRESTORE_API_VERSION,
        )

    @property
    def access_token(self):
        return self.firebase_app.credential.get_access_token().access_token

    def fetch_async(self, url, payload=None, method=None):

        if not method:
            method = 'GET'

        if payload and not isinstance(payload, bytes):
            payload = json.dumps(payload)

        return ndb.get_context().urlfetch(
            url,
            deadline=self.REQUEST_TIMEOUT,
            headers={
                'Authorization': 'Bearer {}'.format(self.access_token),
                'Content-Type': 'application/json',
            },
            method=method,
            payload=payload,
        )

    def create_document(self, collection_id, document_id, fields):
        document_resource = '{}/databases/{}/documents/{collection_id}?documentId={document_id}'.format(
            self.project_path,
            self.database_name,
            collection_id=collection_id,
            document_id=document_id,
        )

        return self.fetch_async(
            '{}/{}'.format(self.firestore_api_url, document_resource),
            method='POST',
            payload={
                'fields': fields
            }
        )

    def delete_document(self, collection_id, document_id):
        return self.fetch_async(
            '{}/{}/databases/{}/documents/{collection_id}/{document_id}'.format(
                self.firestore_api_url,
                self.project_path,
                self.database_name,
                collection_id=collection_id,
                document_id=document_id,
            ),
            method='DELETE'
        )

    def get_by_document_id(self, collection_id, document_id):
        return self.fetch_async(
            '{}/{}/databases/{}/documents/{collection_id}/{document_id}'.format(
                self.firestore_api_url,
                self.project_path,
                self.database_name,
                collection_id=collection_id,
                document_id=document_id,
            )
        )

    def list(self, collection_id, page_size=100, page_token=None):
        return self.fetch_async(
            '{}/{}/databases/{}/documents/{collection_id}?pageSize={page_size}&pageToken={page_token}'.format(
                self.firestore_api_url,
                self.project_path,
                self.database_name,
                collection_id=collection_id,
                page_size=page_size,
                page_token=page_token or '',
            )
        )

    @staticmethod
    def get_document_key(document):
        return document['name'].split('/')[-1]

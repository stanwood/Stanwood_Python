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
"""
Script dumps all firebase security rules to csv file. Requires client secrets to be downloaded from any project.
Client secrets are required to run Oauth2 flow to obtain your credentials to list projects you have access to.
Read more here: https://developers.google.com/api-client-library/python/guide/aaa_overview#2-authorized-api-access-oauth-20

"""

import csv

import firebase_admin
import httplib2
import requests
from googleapiclient.discovery import build
from oauth2client import tools
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage

resource_manager = build('cloudresourcemanager', 'v1')

scopes = [
    'https://www.googleapis.com/auth/cloud-platform',
    'https://www.googleapis.com/auth/userinfo.email',
]

flow = flow_from_clientsecrets(
    'client_secrets.json',
    scope=scopes,
    redirect_uri='http://localhost'
)

storage = Storage('credentials')

credentials = storage.get()
if not credentials:
    credentials = tools.run_flow(flow, storage)

http = credentials.authorize(httplib2.Http())
request = resource_manager.projects().list()
projects = request.execute(http=http)
projects = projects['projects']


with open('rules.csv', 'w') as output_file:
    writer = csv.writer(output_file)

    for project in projects:
        project_id = project['projectId']
        print(project_id)

        firebase_admin_app = firebase_admin.initialize_app(name=project_id)
        token = firebase_admin_app.credential.get_access_token().access_token
        rules = requests.get(
            'https://{}.firebaseio.com/.settings/rules.json?access_token={}'.format(
                project_id,
                token
            )
        )

        if rules.status_code < 399:
            print(' found')
            writer.writerow(
                [
                    project_id,
                    rules.content
                ]
            )
        else:
            print(' not found')
            writer.writerow(
                [
                    project_id,
                    'Not found - probably no firebase project'
                ]
            )

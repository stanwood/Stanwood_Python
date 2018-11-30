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
import logging
import requests


class TogglError(Exception):
    pass


class TogglNotFoundError(TogglError):
    pass


class Toggl(object):

    REPORTS_URL = 'https://toggl.com/reports/api/v2/'
    API_URL = 'https://www.toggl.com/api/v8/'
    USER_AGENT = 'foo@bar.com'
    DATE_FORMAT = '%Y-%m-%d'

    def __init__(self, token, workspace):
        self.token = token
        self.workspace = workspace

    def _fetch(self, url, params=None, method='GET'):
        if not params:
            params = {}

        params['user_agent'] = self.USER_AGENT
        params['workspace_id'] = self.workspace

        request_arguments = {
            'url': url,
            'method': method,
            'auth': (self.token, 'api_token'),
            'timeout': 60
        }

        if method in ('POST', 'PUT'):
            request_arguments['json'] = params
        else:
            request_arguments['params'] = params

        logging.debug(json.dumps(request_arguments, indent=2))

        response = requests.request(**request_arguments)

        # TODO: handle too many requests (429)

        try:
            logging.debug(
                'Response: \n{}'.format(
                    json.dumps(response.json(), indent=2)
                )
            )
            return response.json()
        except ValueError as value_error:
            logging.error('Could not parse {}'.format(response.content))
            raise

    def weekly(self, **params):

        return self._fetch(self.REPORTS_URL + 'weekly', params=params)

    def api(self, endpoint, **params):

        return self._fetch(self.API_URL + endpoint, params)

    def summary(self, **params):

        return self._fetch(self.REPORTS_URL + 'summary', params=params)

    def detailed(self, **params):
        page = 1
        while True:
            results = self.detailed_page(page, **params)
            if results['data']:
                yield results
                page += 1
            else:
                break

    def detailed_page(self, page, **params):
        params['page'] = page
        return self._fetch(
            self.REPORTS_URL + 'details',
            params=params
        )

    @property
    def projects(self):
        return self.api('workspaces/{}/projects'.format(self.workspace), active='both')

    @property
    def users(self):
        return self.api('workspaces/{}/workspace_users'.format(self.workspace))

    def get_user_by_email(self, email):
        users = self._fetch(self.API_URL + 'workspaces/{}/workspace_users'.format(self.workspace))
        try:
            return filter(lambda u: u['email'] == email, users)[0]
        except IndexError:
            raise TogglNotFoundError(u"User not found by email `{}`".format(email))

    def get_current_task(self):
        return self._fetch(self.API_URL + 'time_entries/current')['data']

    def get_project(self, project_id):
        return self._fetch(self.API_URL + 'projects/{}'.format(project_id))['data']

    def get_current_task_project(self):
        current_task = self.get_current_task()
        try:
            if str(current_task['wid']) != self.workspace:
                return None
            project = self.get_project(current_task['pid'])
            return project
        except (TypeError, KeyError):
            return None

    def stop_timer(self, task_id):
        self._fetch(self.API_URL + 'time_entries/{}/stop'.format(task_id), method='PUT')

    def get_project_by_prefix(self, project_name_prefix):
        projects = self._fetch(self.API_URL + '/workspaces/{}/projects'.format(self.workspace))
        try:
            return filter(lambda project: project['name'].startswith(project_name_prefix+' '), projects)[0]
        except IndexError:
            raise TogglNotFoundError('No project name starts with {}'.format(project_name_prefix))

    def get_tasks(self, project_id):
        return self._fetch(self.API_URL + 'projects/{}/tasks'.format(project_id))

    def get_task_by_name(self, project_id, task_name):
        tasks = self.get_tasks(project_id)
        try:
            return filter(lambda task: task['name'] == task_name, tasks)[0]
        except (IndexError, TypeError):
            raise TogglNotFoundError('Task {} not found in project {}'.format(task_name, project_id))

    def start_time_entry(self, task_id, project_id, description, tags=None, billable=False):
        if not tags:
            tags = []

        return self._fetch(
            url=self.API_URL + 'time_entries/start',
            method='POST',
            params={
                'time_entry': {
                    'description': description,
                    'pid': project_id,
                    'tid': task_id,
                    'created_with': 'stanwood-jira-bot',
                    'tags': tags,
                    'billable': billable
                }
            }
        )

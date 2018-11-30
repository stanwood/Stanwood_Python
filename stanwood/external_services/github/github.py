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
import base64
import json
import logging

from google.appengine.api import urlfetch


class GithubError(Exception):
    pass


class Github(object):

    BASE_URL = 'https://api.github.com'

    def __init__(self, repository, token):
        self._repository = repository
        self._token = token

    def _fetch(self, endpoint, **kwargs):
        try:
            kwargs['headers']
        except KeyError:
            kwargs['headers'] = {}

        try:
            if isinstance(kwargs['payload'], dict):
                kwargs['payload'] = json.dumps(kwargs['payload'])
        except KeyError:
            pass

        kwargs['headers'].update({
            # 'Accept': 'application/vnd.github.machine-man-preview+json',
            'Authorization': 'token {}'.format(self._token),
        })

        url = '{}{}'.format(self.BASE_URL, endpoint)
        logging.debug(url)
        logging.debug(json.dumps(kwargs, indent=2))

        response = urlfetch.fetch(url, **kwargs)
        status_code = response.status_code
        if response.content:
            response = json.loads(response.content)
            logging.debug(u'{}\n{}'.format(status_code, json.dumps(response, indent=2)))

            if 'errors' in response:
                raise GithubError(
                    u'\n'.join(
                        error['message']
                        for error in response['errors']
                    )
                )

        if status_code / 400:
            raise GithubError(
                response['message']
            )

        return response

    def create_branch(self, trunk_sha, branch_name):
        return self._fetch(
            '/repos/{}/git/refs'.format(self._repository),
            payload={
                'ref': 'refs/heads/{}'.format(branch_name),
                'sha': trunk_sha
            },
            method='POST'
        )

    def delete_branch(self, ref):
        self._fetch(
            '/repos/{}/git/{}'.format(self._repository, ref),
            method='DELETE'
        )

    def create_pull_request(self, source_branch, base, title):
        pull_request = self._fetch(
            '/repos/{}/pulls'.format(self._repository),
            payload=json.dumps(
                {
                    'base': base,
                    'head': source_branch,
                    'title': title
                }
            ),
            method='POST'
        )

        return pull_request

    def approve_pull_request(self, number):
        return self._fetch(
            '/repos/{}/pulls/{}/reviews'.format(self._repository, number),
            payload={
                'event': 'APPROVE'
            },
            method='POST'
        )

    def merge_pull_request(self, number):
        return self._fetch(
            '/repos/{}/pulls/{}/merge'.format(self._repository, number),
            method='PUT'
        )

    def get_branch(self, branch_name):
        return self._fetch(
            '/repos/{}/git/refs/heads/{}'.format(
                self._repository,
                branch_name
            )
        )

    def create_release(self, tag_name, commit_sha, name, body):
        return self._fetch(
            '/repos/{}/releases'.format(self._repository),
            payload={
                'tag_name': tag_name,
                'target_commitsh': commit_sha,
                'name': name,
                'body': body
            },
            method='POST'
        )

    def get_content(self, path, branch_ref):
        return self._fetch(
            '/repos/{}/contents/{}?ref={}'.format(
                self._repository,
                path,
                branch_ref
            )
        )

    def set_content(self, path, branch_ref, sha, content, message):
        return self._fetch(
            '/repos/{}/contents/{}'.format(self._repository, path),
            payload={
                'branch': branch_ref,
                'content': content,
                'message': message,
                'sha': sha
            },
            method='PUT',
        )

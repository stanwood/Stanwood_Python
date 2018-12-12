import abc

import webapp2
from oauth2client import client
from google.appengine.ext import ndb

import config


class GoogleCalendarBase(object):
    SCOPE = 'https://www.googleapis.com/auth/calendar.events'

    @property
    def redirect_url(self):
        url = '{base_url}/v1/google-calendar/oauth2callback'.format(
            base_url=self.request.host_url,
        )
        if not url.startswith('https://'):
            url = url.replace('http', 'https', 1)
        return url

    @property
    def flow(self):
        return client.OAuth2WebServerFlow(
            client_id=config.GOOGLE_OAUTH_CLIENT_ID,
            client_secret=config.GOOGLE_OAUTH_SECRET_KEY,
            scope=self.SCOPE,
            redirect_uri=self.redirect_url,
            access_type='offline',
            approval_prompt='force'
        )


class AuthorizeHandler(GoogleCalendarBase, webapp2.RequestHandler):

    def get(self):
        key = self.request.get('key')
        if not key:
            self.abort(400, 'Missing key parameter.')

        self.redirect(
            self.flow.step1_get_authorize_url(state=key)
        )


class CallbackHandler(GoogleCalendarBase, webapp2.RequestHandler):

    __metaclass__ = abc.ABCMeta

    @property
    def code(self):
        return self.request.get('code')

    @property
    def state(self):
        return self.request.get('state')

    @property
    def confirm_state(self):
        try:
            return ndb.Key(urlsafe=self.state).get()
        except Exception:
            return None

    @abc.abstractmethod
    def save_tokens(self, refresh_token):
        pass

    def get(self):
        if not self.code:
            self.abort(400, 'Missing code parameter.')

        if not self.state:
            self.abort(400, 'Missing state parameter.')

        credentials = self.flow.step2_exchange(self.code)

        if not self.confirm_state:
            self.abort(400, 'Wrong state parameter.')

        self.save_tokens(
            credentials.refresh_token
        )

        self.response.content_type = 'application/json'
        self.response.json = {
            'success': 'The request was processed successfully.'
        }

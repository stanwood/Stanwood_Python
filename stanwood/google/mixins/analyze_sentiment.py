import logging

import requests
import webapp2
from google.appengine.api import app_identity


class GoogleAPI(object):

    SCOPES = (
        'https://www.googleapis.com/auth/cloud-language',
        'https://www.googleapis.com/auth/cloud-platform',
    )

    @webapp2.cached_property
    def google_auth_token(self):
        auth_token, _ = app_identity.get_access_token(
            self.SCOPES
        )
        return auth_token

    def analyze_sentiment(self, text):
        """
        API Reference:
            https://cloud.google.com/natural-language/docs/reference/rest/v1beta2/documents/analyzeSentiment
        """
        url = 'https://language.googleapis.com/v1beta2/documents:analyzeSentiment'

        response = requests.post(
            url,
            json={
                'document': {
                  'type': 'PLAIN_TEXT',
                  'language': 'en',
                  'content': text,
                }
            },
            headers={'Authorization': 'Bearer {}'.format(self.google_auth_token)}
        )

        if response.status_code / 400:
            logging.error('Google analyzeSentiment is not responding. Response body:\n' + response.content)
            raise webapp2.exc.HTTPBadGateway()

        return response.json()


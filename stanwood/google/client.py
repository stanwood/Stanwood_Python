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
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

import config


class GoogleCalendar(object):

    def __init__(self, refresh_token):
        self.client = self._client(refresh_token)

    @staticmethod
    def _client(refresh_token):
        credentials = Credentials(
            None,
            refresh_token=refresh_token,
            token_uri='https://accounts.google.com/o/oauth2/token',
            client_id=config.GOOGLE_OAUTH_CLIENT_ID,
            client_secret=config.GOOGLE_OAUTH_SECRET_KEY,
            scopes=[
                'https://www.googleapis.com/auth/calendar',
                'https://www.googleapis.com/auth/calendar.events'
            ]
        )

        calendar = build('calendar', 'v3', credentials=credentials)

        return calendar

    def insert_event(self, calendar_id, body):
        """
        API reference:
            https://developers.google.com/calendar/v3/reference/events/insert
        """
        results = self.client.events().insert(
            calendarId=calendar_id,
            body=body,
            sendUpdates='all',
        ).execute()

        return results

    def update_event(self, calendar_id, event_id, body, **kwargs):
        """
        API Reference:
            https://developers.google.com/calendar/v3/reference/events/patch
        """
        results = self.client.events().patch(
            calendarId=calendar_id,
            eventId=event_id,
            body=body,
            **kwargs
        ).execute()
        return results

    def get_event(self, calendar_id, event_id):
        results = self.client.events().get(
            calendarId=calendar_id,
            eventId=event_id,
        ).execute()

        return results

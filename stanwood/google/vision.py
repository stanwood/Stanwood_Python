import base64
import json
import logging
import re

from google.appengine.api import (
    app_identity,
    urlfetch,
)

import dateutil.parser


class OcrModel(object):

    class BaseText(object):

        def __init__(self, pattern):
            self.pattern = pattern

        def search(self, text):
            try:
                return self.pattern.search(text).group(0).strip()
            except AttributeError:
                return None

    class TextAfter(BaseText):

        def __init__(self, a, fmt=r'.*?'):
            super(OcrModel.TextAfter, self).__init__(
                re.compile(
                    r'(?<={})\s*{}'.format(a, fmt),
                    re.UNICODE,
                ),
            )

    class TextBetween(BaseText):

        def __init__(self, a, b, fmt=r'.*?'):
            super(OcrModel.TextBetween, self).__init__(
                re.compile(
                    r'(?<={}){}(?={})'.format(a, fmt, b),
                    re.UNICODE | re.DOTALL,
                ),
            )

    class StringField(TextBetween):

        def __init__(self, a, b):
            super(OcrModel.StringField, self).__init__(
                r'\n{}[\.,]'.format(a),
                r'\n{}[\.,]'.format(b),
            )

    class DateField(TextAfter):

        def __init__(self, a):
            super(OcrModel.DateField, self).__init__(
                r'\n{}[\.,]'.format(a),
                r'\d{2}[\.-]\d{2}[\.-](\d{2}|\d{4})\b',
            )

        def search(self, text):

            value = super(OcrModel.DateField, self).search(text)

            try:
                value = dateutil.parser.parse(
                    value,
                    dayfirst=True,
                )
                value = value.strftime('%d.%m.%Y')
            except (
                TypeError,
                ValueError,
            ):
                value = None

            return value

    def __init__(self, text):

        logging.debug(text)

        for name in dir(self.__class__):

            attr = getattr(self.__class__, name)

            if isinstance(attr, OcrModel.BaseText):
                setattr(self, name, attr.search(text))


class DrivingLicence(OcrModel):

    TITLES = (
        u'MISS ',
        u'MR ',
        u'MRS ',
        u'MS ',
    )

    lastname = OcrModel.StringField('1', '2')
    firstname = OcrModel.StringField('2', '3')
    middlename = None
    title = None
    birthdate = OcrModel.DateField('3')
    issued = OcrModel.DateField('4a')
    expiry = OcrModel.DateField('4b')
    issued_by = OcrModel.TextBetween(
        r'\b4c[\.,]',
        r'\n',
        r'[\w ]+',
    )
    number = OcrModel.TextBetween(
        r'\b5[\.,]',
        r'\n',
        r'[\w\- ]+',
    )
    number_uk = OcrModel.TextBetween(
        r'\b',
        r' \d{2}\n',
        r' *([A-Z9] ?){5}\d ?([05] ?[1-9]|[16] ?[012]) ?(0 ?[1-9]|[12] ?\d|3 ?[01]) ?\d ?([A-Z9] ?){2}\d ?([A-Z] ?){2}(\d ?){0,2}',
    )
    address = OcrModel.StringField('8', '9')
    category = OcrModel.TextBetween(
        '\n9[\.,]',
        '\n',
    )
    city = None
    postal_code = None

    def __init__(self, source=None, content=None):

        if source:
            image = {
                'source': {
                    'gcsImageUri': source,
                }
            }
        else:
            image = {
                'content': base64.b64encode(content),
            }

        access_token = app_identity.get_access_token(
            scopes=(
                'https://www.googleapis.com/auth/cloud-platform',
                'https://www.googleapis.com/auth/cloud-vision',
            ),
        )[0]

        response = urlfetch.fetch(
            'https://vision.googleapis.com/v1p2beta1/images:annotate',
            method='POST',
            payload=json.dumps({
                'requests': [
                    {
                        'image': image,
                        'features': [
                            {
                                'type': 'TEXT_DETECTION',
                            },
                        ],
                        'imageContext': {},
                    }
                ]
            }),
            headers={
                'Authorization': 'Bearer {}'.format(access_token),
                'Content-Type': 'application/json',
            }
        )
        response = json.loads(response.content)

        try:
            source = response['responses'][0]['textAnnotations'][0]['description']
        except LookupError:
            source = ''

        super(DrivingLicence, self).__init__(source)

        if self.firstname:
            self.firstname = self.firstname.replace('\n', ' ')

            for title in self.TITLES:
                if self.firstname.startswith(title):
                    self.firstname = self.firstname.replace(title, u'')
                    self.title = title.rstrip(' ')
                    break

            try:
                self.firstname, self.middlename = self.firstname.split(
                    ' ',
                    1,
                )
            except ValueError:
                pass

        if self.number_uk:
            self.number = self.number_uk

        if self.number:
            self.number = self.number.replace(' ', '')

        if self.address:
            try:
                self.address, self.city, self.postal_code = self.address.rsplit(', ', 2)
            except ValueError:
                pass

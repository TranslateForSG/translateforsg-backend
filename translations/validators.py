from django.core.exceptions import ValidationError
from googleapiclient.errors import HttpError

from translations.imports import validate_rows, EXPECTED_HEADERS, get_sheet_service


def validate_google_sheet_id(google_sheet_id: str):
    sheet = get_sheet_service()

    try:
        result = sheet.values().get(spreadsheetId=google_sheet_id, range='A1:D1').execute()
        values = result.get('values', [])

        if not validate_rows(values[0]):
            raise ValidationError(f'Expected Header to be {EXPECTED_HEADERS}. Found {values[0]}')

        return google_sheet_id
    except HttpError as e:
        if e.resp['status'] == '404':
            raise ValidationError('Google Sheet not found.')
        if e.resp['status'] == '403':
            raise ValidationError('Google Sheet access denied.')

        raise e

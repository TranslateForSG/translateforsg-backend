import logging
from os import environ
from typing import List

from django.apps import apps
from django.db import transaction
from google.oauth2 import service_account
from googleapiclient.discovery import build

logger = logging.getLogger('google_sheets_importer')

HEADER_ID = 'ID'
HEADER_ORIGINAL_PHRASE = 'ENGLISH'
HEADER_TRANSLATED_PHRASE = 'TRANSLATED_TEXT'
HEADER_ROMANIZED_PHRASE = 'ROMANIZED'

EXPECTED_HEADERS = [HEADER_ID, HEADER_ORIGINAL_PHRASE, HEADER_TRANSLATED_PHRASE, '']
EXPECTED_HEADERS_ROMANIZATION = [HEADER_ID, HEADER_ORIGINAL_PHRASE, HEADER_TRANSLATED_PHRASE, HEADER_ROMANIZED_PHRASE]

MODE_BASIC = 0x01
MODE_WITH_ROMANIZATION = 0x02

RANGES = {
    MODE_BASIC: 'A:C',
    MODE_WITH_ROMANIZATION: 'A:D',
}


def get_sheet_service():
    secret_file = environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    credentials = service_account.Credentials.from_service_account_file(secret_file)
    service = build('sheets', 'v4', credentials=credentials)

    logger.info('built service')

    return service.spreadsheets()


def validate_rows(first_row: List[str]):
    if first_row == EXPECTED_HEADERS_ROMANIZATION:
        return MODE_WITH_ROMANIZATION
    if first_row == EXPECTED_HEADERS:
        return MODE_BASIC
    raise ValueError(f'Unexpected header row {first_row}')


def import_now(language_code: str, google_sheet_id: str, raise_exceptions=False):
    service = get_sheet_service()

    logger.info(f'requesting Google Sheet {google_sheet_id} for {language_code}')
    result = service.values().get(spreadsheetId=google_sheet_id, range='A1:D1').execute()
    rows = result.get('values', [])
    mode = validate_rows(rows[0])

    ranges = RANGES[mode]

    logger.info(f'requesting Google Sheet {google_sheet_id} for {language_code} with range {ranges}')
    result = service.values().get(spreadsheetId=google_sheet_id, range=ranges).execute()
    rows = result.get('values', [])

    Translation = apps.get_model('translations', 'Translation')
    Language = apps.get_model('translations', 'Language')

    language = Language.objects.get(code=language_code)

    with transaction.atomic():
        for row in rows[1:]:
            import_single_row(row, mode=mode, language=language, translation_model=Translation)


def import_single_row(row, mode, language, translation_model):
    phrase_id = int(row[0])
    translated_text = row[1]

    data = {}

    if translated_text and translated_text.strip():
        data['content'] = translated_text

    if mode == MODE_WITH_ROMANIZATION and row[2] and row[2].strip():
        data['romanized'] = row[2]

    translation, created = translation_model.objects.update_or_create(
        phrase_id=phrase_id,
        language_id=language.id,
        defaults=data
    )

    if created:
        logger.info(f'Created Translation for #{phrase_id}')
    else:
        logger.info(f'Updated Translation for #{phrase_id}')

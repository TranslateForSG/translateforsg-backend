import csv
import hashlib
import re

from django.core.files import File
from django.core.management.base import BaseCommand
from django.db import IntegrityError
from google_drive_downloader import GoogleDriveDownloader as gdd

from translations.models import Translation, Language, Phrase

GDRIVE_PATTERN_0 = re.compile(r'file\/d\/(.*)\/view')
GDRIVE_PATTERN_1 = re.compile(r'open\?id\=(.*)')


class Command(BaseCommand):
    help = 'Imports Translation from file'

    def add_arguments(self, parser):
        parser.add_argument('lang')
        parser.add_argument('csv_file')
        parser.add_argument('audio_format')

    def extract_id(self, google_drive_uri: str):
        if google_drive_uri.startswith('https://drive.google.com/file'):
            return GDRIVE_PATTERN_0.search(google_drive_uri).groups()[0]
        if google_drive_uri.startswith('https://drive.google.com/open'):
            return GDRIVE_PATTERN_1.search(google_drive_uri).groups()[0]
        return google_drive_uri

    def process_row(self, language, row, audio_format):
        phrases = Phrase.objects.filter(content=row['ENGLISH'])

        for phrase in phrases:
            t = self.create_translation(audio_format, language, phrase, row)
            if t:
                print(t.id, t.phrase.content)

    def create_translation(self, audio_format, language, phrase, row):
        if Translation.objects.filter(phrase=phrase, language=language).exists():
            return

        t = Translation(content=row['TRANSLATED_TEXT'], language=language, phrase=phrase)
        audio_url = row.get('AUDIO_URL')

        if audio_url:
            tmp_path = self.download_audio(audio_format, audio_url)
            md5 = hashlib.md5(row['TRANSLATED_TEXT'].encode()).hexdigest()

            with open(tmp_path, 'rb') as f:
                t.audio_clip.save(f'{md5}.{audio_format}', File(f))
        try:
            t.save()
        except IntegrityError:
            self.stderr.write(f'FAIL for {row["ENGLISH"]}')
        return t

    def download_audio(self, audio_format, audio_url):
        tmp_path = f'/tmp/translateforsg/audio.{audio_format}'
        gdd.download_file_from_google_drive(file_id=self.extract_id(audio_url),
                                            dest_path=tmp_path, overwrite=True)
        return tmp_path

    def handle(self, *args, **options):
        with open(options['csv_file'], newline='') as csvfile:
            reader = csv.DictReader(csvfile)

            language = Language.objects.get(code=options['lang'])

            for row in reader:
                self.process_row(language, row, options['audio_format'])

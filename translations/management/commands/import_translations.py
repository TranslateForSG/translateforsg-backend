import csv
import hashlib
import re

from django.core.files import File
from django.core.management.base import BaseCommand
from django.db import IntegrityError
from google_drive_downloader import GoogleDriveDownloader as gdd

from translations.models import Translation, Language, Phrase

PATTERN = re.compile(r'file\/d\/(.*)\/view')
PATTERN2 = re.compile(r'file\/d\/(.*)\/view')


class Command(BaseCommand):
    help = 'Imports Translation from file'

    def add_arguments(self, parser):
        parser.add_argument('lang')
        parser.add_argument('csv_file')

    def extract_id(self, google_drive_uri: str):
        if google_drive_uri.startswith('https://drive.google.com/file'):
            return PATTERN.search(google_drive_uri).groups()[0]
        if google_drive_uri.startswith('https://drive.google.com/open'):
            return PATTERN2.search(google_drive_uri).groups()[0]
        return google_drive_uri

    def process_row(self, language, row):
        phrases = Phrase.objects.filter(content=row['ENGLISH'])

        for phrase in phrases:

            if Translation.objects.filter(phrase=phrase, language=language).exists():
                continue

            t = Translation(content=row['TRANSLATED_TEXT'], language=language, phrase=phrase)

            audio_url = row.get('AUDIO_URL')
            if audio_url:
                gdd.download_file_from_google_drive(file_id=self.extract_id(audio_url),
                                                    dest_path='/tmp/translateforsg/audio.mp3')
                md5 = hashlib.md5(row['TRANSLATED_TEXT'].encode()).hexdigest()
                with open('/tmp/translateforsg/audio.mp3', 'rb') as f:
                    t.audio_clip.save(f'{md5}.mp3', File(f))
            try:
                t.save()
            except IntegrityError:
                self.stderr.write(f'FAIL for {row["ENGLISH"]}')
            print(t.id, t.phrase.content)

    def handle(self, *args, **options):
        with open(options['csv_file'], newline='') as csvfile:
            reader = csv.DictReader(csvfile)

            language = Language.objects.get(code=options['lang'])

            for row in reader:
                self.process_row(language, row)

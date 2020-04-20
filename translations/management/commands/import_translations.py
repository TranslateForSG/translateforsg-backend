import csv
import re

from django.core.management.base import BaseCommand

from translations.models import Translation, Language, Phrase

PATTERN = re.compile(r'file\/d\/(.*)\/view')


class Command(BaseCommand):
    help = 'Imports Translation from file'

    def add_arguments(self, parser):
        parser.add_argument('lang')
        parser.add_argument('csv_file')

    def process_row(self, language, row):
        phrases = Phrase.objects.filter(content=row['ENGLISH'])

        for phrase in phrases:
            t = Translation(content=row['TRANSLATED_TEXT'], language=language, phrase=phrase)
            # md5 = hashlib.md5(row['TRANSLATED_TEXT'].encode()).hexdigest()
            # t.audio_clip.save(f'{md5}.mp3', File(open('/tmp/translateforsg/audio.mp3', 'rb')))
            t.save()
            print(t.id, t.phrase.content)

    def handle(self, *args, **options):
        with open(options['csv_file'], newline='') as csvfile:
            reader = csv.DictReader(csvfile)

            language = Language.objects.get(code=options['lang'])

            for row in reader:
                self.process_row(language, row)

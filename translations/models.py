import hashlib
from uuid import uuid4

from django.conf import settings
from django.db import models
from django.utils.datetime_safe import datetime
from django.utils.text import slugify

from translations.audio_generation import generate_audio_file
from translations.consts import DAYS_OF_WEEK, ETHNICITY_LIST


class Language(models.Model):
    name = models.CharField(max_length=50)
    native_name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, db_index=True, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100)
    parent_category = models.ForeignKey('Category', blank=True, null=True, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name


class Phrase(models.Model):
    summary = models.CharField(max_length=100)
    content = models.TextField()
    category = models.ForeignKey('Category', on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.summary


class Translation(models.Model):
    phrase = models.ForeignKey('Phrase', on_delete=models.CASCADE)

    language = models.ForeignKey('Language', on_delete=models.CASCADE)
    content = models.TextField()
    audio_clip = models.FileField(
        blank=True,
        help_text='Optional, will be auto generated if not provided.',
        upload_to='recorded_clips/'
    )
    special_note = models.TextField(verbose_name='Special note to doctor (if needed)', blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.phrase.summary} for {self.language.name}'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):

        if not self.audio_clip:
            filename = hashlib.md5(self.content.encode()).hexdigest()
            content = generate_audio_file(self.content, self.language.code)
            self.audio_clip.save(filename + '.mp3', content)
            self.is_audio_generated = True
        super().save(force_insert, force_update, using, update_fields)

    class Meta:
        unique_together = ('language', 'phrase')


class Volunteer(models.Model):
    uuid = models.UUIDField(unique=True, db_index=True, default=uuid4)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    display_name = models.CharField(max_length=50)

    language = models.ForeignKey('Language', on_delete=models.PROTECT)
    phone_number = models.CharField(max_length=20)
    availability = models.NullBooleanField()
    availability_slots = models.ManyToManyField('AvailabilitySlot', blank=True)
    ethnicity = models.CharField(max_length=15, choices=[(e, e) for e in ETHNICITY_LIST], default='Bangladeshi')

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.display_name

    @staticmethod
    def get_available_volunteers(time: datetime = None):

        if time is None:
            time = datetime.now()

        return Volunteer.objects.filter(availability_slots__day=time.strftime('%A'),
                                        availability_slots__start_time__lt=time.time(),
                                        availability_slots__end_time__gt=time.time())


class AvailabilitySlot(models.Model):
    day = models.CharField(max_length=10, choices=[(d, d) for d in DAYS_OF_WEEK])

    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f'{self.day} ({self.start_time} - {self.end_time})'

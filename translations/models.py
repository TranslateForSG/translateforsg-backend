import hashlib

from adminsortable.fields import SortableForeignKey
from adminsortable.models import SortableMixin
from django.db import models

from translations.audio_generation import generate_audio_file, generate_translation


class Language(models.Model):
    name = models.CharField(max_length=50)
    native_name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, db_index=True, unique=True)
    speaking_rate = models.DecimalField(max_digits=3, decimal_places=2, default=0.85)

    translation_code = models.CharField(max_length=10, blank=True, db_index=True,
                                        help_text='Translation will not be generated if blank')
    speech_code = models.CharField(max_length=10, blank=True, db_index=True,
                                   help_text='Speech will not be generated if blank')

    is_active = models.BooleanField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def fill_in_untranslated(self):
        all_phrases = set(Phrase.objects.values_list('id', flat=True))
        translated_phrases = set(Phrase.objects.filter(translation__language=self).values_list('id', flat=True))

        remaining_ids = list(all_phrases - translated_phrases)
        remaining_phrases = Phrase.objects.filter(pk__in=remaining_ids)

        for phrase in remaining_phrases:
            translation = Translation(language=self, phrase=phrase)
            translation.save()

        return remaining_ids

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.translation_code = self.code
        super().save(force_insert, force_update, using, update_fields)


class Category(SortableMixin):
    name = models.CharField(max_length=100)
    parent_category = models.ForeignKey('Category', blank=True, null=True, on_delete=models.CASCADE)

    intended_for = models.ManyToManyField('UserType', blank=True)

    is_active = models.BooleanField()
    needs_original_phrase = models.NullBooleanField()
    order = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'categories'
        ordering = ['order']

    def __str__(self):
        return self.name


class Phrase(SortableMixin):
    summary = models.CharField(max_length=100)
    content = models.TextField()
    categories = models.ManyToManyField('Category', through='PhraseCategory', related_query_name='phrases',
                                        related_name='phrase')
    order = models.PositiveIntegerField(editable=False, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.summary

    class Meta:
        ordering = ['order']


class Translation(models.Model):
    phrase = models.ForeignKey('Phrase', on_delete=models.CASCADE)

    language = models.ForeignKey('Language', on_delete=models.CASCADE)
    content = models.TextField(blank=True)
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

        self.translate()
        self.synthesize()

        super().save(force_insert, force_update, using, update_fields)

    def synthesize(self):
        if not self.audio_clip and self.language.speech_code:
            filename = hashlib.md5(self.content.encode()).hexdigest()
            content = generate_audio_file(self.content, self.language.speech_code, self.language.speaking_rate)
            self.audio_clip.save(filename + '.mp3', content)

    def translate(self):
        if not self.content.strip() and self.language.translation_code:
            self.content = generate_translation(text=self.phrase.content,
                                                target_language=self.language.translation_code)

    class Meta:
        unique_together = ('language', 'phrase')


class Contributor(models.Model):
    name = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class UserType(SortableMixin):
    name = models.CharField(max_length=100)
    order = models.PositiveIntegerField(editable=False, db_index=True, default=0)

    is_active = models.BooleanField()
    needs_original_phrase = models.NullBooleanField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['order']


class PhraseCategory(SortableMixin):
    category = SortableForeignKey('Category', on_delete=models.CASCADE, db_index=True)
    phrase = models.ForeignKey('Phrase', on_delete=models.CASCADE, db_index=True)
    order = models.PositiveIntegerField(editable=False, db_index=True, default=0)

    def __str__(self):
        return f'{self.category.name} - {self.phrase.content}'

    class Meta:
        ordering = ['order']


class TranslationFeedback(models.Model):
    translation = models.ForeignKey('Translation', on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=True)
    whats_wrong = models.TextField(blank=True)
    suggestion = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def accept(self):
        trans = self.translation

        trans.content = self.suggestion
        trans.audio_clip = None
        trans.save()

        # automatically add ot contributors
        Contributor.objects.get_or_create(name=self.name)

import hashlib

from adminsortable.fields import SortableForeignKey
from adminsortable.models import SortableMixin
from django.db import models
from django_fsm import FSMField, transition

from translations.audio_generation import generate_audio_file, generate_translation
from translations.imports import import_now
from translations.validators import validate_google_sheet_id


class Language(models.Model):
    name = models.CharField(max_length=50)
    native_name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, db_index=True, unique=True)
    speaking_rate = models.DecimalField(max_digits=3, decimal_places=2, default=0.85)

    translation_code = models.CharField(max_length=10, blank=True, db_index=True,
                                        help_text='Translation will not be generated if blank')
    speech_code = models.CharField(max_length=10, blank=True, db_index=True,
                                   help_text='Speech will not be generated if blank')

    google_sheet_id = models.CharField(max_length=50, blank=True,
                                       verbose_name='Google Sheet ID',
                                       validators=[validate_google_sheet_id])

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

    def import_sheet(self):
        assert self.google_sheet_id

        job = TranslationImportJob.objects.create(
            language=self,
            google_sheet_id=self.google_sheet_id
        )

        job.start_processing()
        job.save()

        try:
            import_now(self.code, self.google_sheet_id)
        except BaseException as e:
            job.mark_fail()
            job.save()
            raise e

        job.mark_success()
        job.save()


class TranslationImportJob(models.Model):
    language = models.ForeignKey('Language', on_delete=models.CASCADE)
    google_sheet_id = models.CharField(max_length=50)

    status = FSMField(default='new')
    updated_rows = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @transition(field=status, source='new', target='in_progress')
    def start_processing(self):
        pass

    @transition(field=status, source='in_progress', target='successful')
    def mark_success(self):
        pass

    @transition(field=status, source='in_progress', target='failed')
    def mark_fail(self):
        pass


class Categorizable(SortableMixin):
    name = models.CharField(max_length=100)

    intended_for = models.ManyToManyField('UserType', blank=True)

    is_active = models.BooleanField()
    needs_original_phrase = models.NullBooleanField()
    order = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']
        abstract = True

    def __str__(self):
        return self.name


class Section(Categorizable):
    class Meta:
        ordering = ['order']


class Category(Categorizable):
    section = models.ForeignKey('Section', blank=False, null=True, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = 'categories'
        ordering = ['order']


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
    romanized = models.TextField(blank=True)
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
    status = FSMField(protected=True, default='new')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @transition(field=status, source='new', target='accepted')
    def accept(self):
        trans = Translation.objects.get(pk=self.translation_id)

        trans.content = self.suggestion
        trans.audio_clip = None
        trans.save()

        # automatically add ot contributors
        Contributor.objects.get_or_create(name=self.name)

    @transition(field=status, source='new', target='rejected')
    def reject(self):
        pass

    @transition(field=status, source='new', target='passed')
    def passover(self):
        pass


class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Downloadable(models.Model):
    name = models.CharField(max_length=60)
    description = models.TextField(blank=True)

    language = models.ForeignKey('Language', on_delete=models.CASCADE)
    category = models.ForeignKey('Category', blank=True, null=True, on_delete=models.CASCADE)
    downloadable_file = models.FileField(upload_to='downloadables/')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

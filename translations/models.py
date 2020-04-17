from django.db import models


class Language(models.Model):
    name = models.CharField(max_length=50)
    native_name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, db_index=True, unique=True)


class Category(models.Model):
    name = models.CharField(max_length=100)


class Phrase(models.Model):
    summary = models.CharField(max_length=100)
    content = models.TextField()
    category = models.ForeignKey('Category', on_delete=models.CASCADE)


class Translation(Phrase):
    language = models.ForeignKey('Language', on_delete=models.CASCADE)
    special_note = models.TextField(verbose_name='Special note to doctor (if needed)', blank=True)
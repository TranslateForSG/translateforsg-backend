from django.apps import AppConfig
from django.db.models.signals import post_save

from translations.signals import clear_default_cache


class TranslationsConfig(AppConfig):
    name = 'translations'

    def ready(self):
        super().ready()

        from translations.models import Language, UserType, Contributor, Section, Category
        post_save.connect(clear_default_cache, sender=Language)
        post_save.connect(clear_default_cache, sender=UserType)
        post_save.connect(clear_default_cache, sender=Contributor)
        post_save.connect(clear_default_cache, sender=Section)
        post_save.connect(clear_default_cache, sender=Category)

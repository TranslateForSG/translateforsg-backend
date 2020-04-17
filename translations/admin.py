from django.contrib import admin
from .models import Language, Category, Phrase, Translation


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ['name', 'native_name', 'code']

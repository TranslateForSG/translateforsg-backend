from django.contrib import admin
from reversion.admin import VersionAdmin

from .models import Language, Category, Phrase, Translation


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ['name', 'native_name', 'code']
    search_fields = ['name', 'native_name', 'code']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


class TranslationInlineAdmin(admin.StackedInline):
    model = Translation
    fields = ['language', 'content', 'special_note']
    extra = 0


@admin.register(Phrase)
class PhraseAdmin(VersionAdmin):
    list_display = ['summary', 'category', 'updated_at']
    search_fields = ['summary', 'content']
    inlines = [TranslationInlineAdmin]
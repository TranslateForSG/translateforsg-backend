from adminsortable.admin import SortableTabularInline, SortableStackedInline, NonSortableParentAdmin
from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from reversion.admin import VersionAdmin

from .models import Language, Category, Phrase, Translation


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ['name', 'native_name', 'code']
    search_fields = ['name', 'native_name', 'code']
    readonly_fields = ['created_at', 'updated_at']


class PhraseInlineAdmin(SortableTabularInline):
    model = Phrase
    fields = ['summary', 'content', 'change_link']
    extra = 0
    readonly_fields = ['summary', 'content', 'change_link', 'created_at', 'updated_at']

    def change_link(self, obj):
        return mark_safe('<a href="%s">Full edit</a>' % \
                         reverse('admin:translations_phrase_change',
                                 args=(obj.id,)))


@admin.register(Category)
class CategoryAdmin(NonSortableParentAdmin):
    list_display = ['name', 'parent_category']
    search_fields = ['name']
    list_filter = ['parent_category']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [PhraseInlineAdmin]


class TranslationInlineAdmin(admin.StackedInline):
    model = Translation
    fields = ['language', 'content', 'special_note', 'audio_clip']
    extra = 0
    readonly_fields = ['created_at', 'updated_at']


class PhraseResource(resources.ModelResource):
    class Meta:
        model = Phrase
        exclude = ['id']


@admin.register(Phrase)
class PhraseAdmin(ImportExportModelAdmin, VersionAdmin):
    list_display = ['summary', 'category', 'content', 'updated_at']
    search_fields = ['summary', 'content']
    list_filter = ['category']
    inlines = [TranslationInlineAdmin]
    readonly_fields = ['created_at', 'updated_at']
    resource_class = PhraseResource

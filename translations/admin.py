from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from reversion.admin import VersionAdmin

from .models import Language, Category, Phrase, Translation, Volunteer, AvailabilitySlot


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ['name', 'native_name', 'code']
    search_fields = ['name', 'native_name', 'code']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']


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


@admin.register(Volunteer)
class VolunteerAdmin(VersionAdmin):
    list_display = ['display_name', 'language', 'availability']
    search_fields = ['display_name']
    list_filter = ['availability', 'language']
    exclude = ['uuid', 'availability']
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['availability_slots']


admin.site.register(AvailabilitySlot)

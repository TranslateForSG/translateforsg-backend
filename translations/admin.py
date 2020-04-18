from django.contrib import admin
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


@admin.register(Phrase)
class PhraseAdmin(VersionAdmin):
    list_display = ['summary', 'category', 'updated_at']
    search_fields = ['summary', 'content']
    inlines = [TranslationInlineAdmin]
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Volunteer)
class VolunteerAdmin(VersionAdmin):
    list_display = ['display_name', 'language', 'availability']
    search_fields = ['display_name']
    list_filter = ['availability', 'language']
    exclude = ['uuid', 'availability']
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['availability_slots']


admin.site.register(AvailabilitySlot)

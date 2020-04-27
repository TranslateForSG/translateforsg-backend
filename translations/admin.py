from adminsortable.admin import SortableTabularInline, SortableAdmin
from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe
from fsm_admin.mixins import FSMTransitionMixin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from reversion.admin import VersionAdmin

from .forms import PhraseForm
from .models import Language, Category, Phrase, Translation, Contributor, PhraseCategory, UserType, TranslationFeedback, \
    Contact, Downloadable, Section


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ['name', 'native_name', 'code', 'is_active']
    search_fields = ['name', 'native_name', 'code']
    readonly_fields = ['created_at', 'updated_at']
    list_filter = ['is_active']


class PhraseInlineAdmin(SortableTabularInline):
    model = PhraseCategory
    fields = ['content', 'change_link']
    readonly_fields = ['content', 'change_link']
    extra = 0

    def content(self, obj):
        return obj.phrase.content

    def change_link(self, obj):
        url = reverse('admin:translations_phrase_change', args=(obj.phrase_id,))
        return mark_safe('<a href="%s">Edit</a>' % url)


class CategoryInlineAdmin(SortableTabularInline):
    model = Category
    fields = ['name', 'change_link']
    readonly_fields = ['change_link']
    extra = 0

    def change_link(self, obj):
        url = reverse('admin:translations_category_change', args=(obj.id,))
        return mark_safe('<a href="%s">Edit</a>' % url)

    def has_add_permission(self, request, obj):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Section)
class SectionAdmin(SortableAdmin):
    list_display = ['name', 'is_active']
    search_fields = ['name']
    list_filter = ['intended_for', 'is_active']
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['intended_for']
    inlines = [CategoryInlineAdmin]


@admin.register(Category)
class CategoryAdmin(SortableAdmin):
    list_display = ['name', 'is_active']
    search_fields = ['name']
    list_filter = ['intended_for', 'is_active']
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['intended_for']
    inlines = [PhraseInlineAdmin]


class TranslationInlineAdmin(admin.StackedInline):
    model = Translation
    fields = ['language', 'content', 'special_note', 'audio_clip']
    extra = 0
    readonly_fields = ['created_at', 'updated_at']


class TranslationFeedbackInline(admin.StackedInline):
    model = TranslationFeedback
    fields = ['name', 'whats_wrong', 'suggestion']
    extra = 0


@admin.register(Translation)
class TranslationAdmin(admin.ModelAdmin):
    search_fields = ['translation__phrase__summary', 'translation__phrase', 'content']
    list_display = ['content']
    inlines = [TranslationFeedbackInline]


class PhraseResource(resources.ModelResource):
    english = resources.Field(attribute='content', column_name='ENGLISH')
    translated_text = resources.Field(column_name='TRANSLATED_TEXT', default='')
    audio_url = resources.Field(column_name='AUDIO_URL', default='')

    class Meta:
        model = Phrase
        fields = ['english', 'translated_text', 'audio_url']


@admin.register(Phrase)
class PhraseAdmin(ImportExportModelAdmin, VersionAdmin):
    list_display = ['summary', 'content', 'updated_at']
    list_filter = ['categories']
    search_fields = ['summary', 'content']
    inlines = [TranslationInlineAdmin]
    form = PhraseForm
    readonly_fields = ['created_at', 'updated_at']
    resource_class = PhraseResource
    ordering = ['categories__first__order', 'order']


@admin.register(Contributor)
class ContributorAdmin(VersionAdmin):
    list_display = ['name']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(UserType)
class UserTypeAdmin(VersionAdmin):
    list_display = ['name', 'is_active']
    search_fields = ['name']
    list_filter = ['is_active']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(TranslationFeedback)
class TranslationFeedbackAdmin(FSMTransitionMixin, admin.ModelAdmin):
    list_display = ['phrase', 'language', 'name', 'created_at']
    readonly_fields = ['name', 'whats_wrong', 'current_translation', 'translation', 'suggestion', 'status']
    fields = ['status', 'name', 'whats_wrong', 'suggestion', 'current_translation', 'translation']
    fsm_field = 'status'
    list_filter = ['status']

    def current_translation(self, obj: TranslationFeedback):
        return obj.translation.content

    def phrase(self, obj: TranslationFeedback):
        return obj.translation.phrase.summary

    def language(self, obj: TranslationFeedback):
        return obj.translation.language


@admin.register(Contact)
class ContactAdmin(VersionAdmin):
    list_display = ['name', 'email', 'created_at']
    search_fields = ['name', 'email', 'content']
    readonly_fields = ['name', 'email', 'content', 'created_at', 'updated_at']
    ordering = ['-created_at']

    def has_add_permission(self, request):
        return False


@admin.register(Downloadable)
class DownloadableAdmin(VersionAdmin):
    list_display = ['name', 'language', 'downloadable_file', 'updated_at']
    list_filter = ['language']
    readonly_fields = ['created_at', 'updated_at']
    search_fields = ['name', 'description']

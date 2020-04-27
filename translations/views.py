from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, viewsets, filters
from rest_framework.exceptions import ValidationError

from translateforsg.pagination import PerPage1000, PerPage100
from translations.filters import TranslationFilterSet
from translations.models import Language, Phrase, Category, Translation, Contributor, UserType, Downloadable
from translations.serializers import PhraseSerializer, LanguageSerializer, CategorySerializer, \
    TranslationSerializerMain, ContributorSerializer, UserTypeSerializer, TranslationFeedbackSecureSerializer, \
    ContactSecureSerializer, DownloadableSerializer


class PhraseViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = PhraseSerializer
    queryset = Phrase.objects.all() \
        .prefetch_related('translation_set', 'translation_set__language', 'categories') \
        .order_by('id')
    pagination_class = PerPage1000
    filter_backends = [filters.SearchFilter]
    search_fields = ['summary', 'content']


class LanguageViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = LanguageSerializer
    queryset = Language.objects.filter(is_active=True).order_by('name')
    pagination_class = PerPage1000


class CategoryViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.filter(is_active=True).order_by('order')
    pagination_class = PerPage1000
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name']
    filterset_fields = ['intended_for', 'intended_for__name']


class TranslationViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = TranslationSerializerMain
    queryset = Translation.objects.all() \
        .select_related('phrase') \
        .prefetch_related('phrase__categories') \
        .order_by('phrase__categories__order', 'phrase__phrasecategory__order')

    pagination_class = PerPage100
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['phrase__summary', 'phrase__content', 'content']
    filterset_class = TranslationFilterSet

    def list(self, request, *args, **kwargs):
        if not self.request.query_params.get('language__name'):
            raise ValidationError({'detail': 'Must provide language as a filter'})
        return super().list(request, *args, **kwargs)


class ContributorViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = ContributorSerializer
    queryset = Contributor.objects.all().order_by('?')
    pagination_class = PerPage1000


class UserTypeViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = UserTypeSerializer
    queryset = UserType.objects.filter(is_active=True).order_by('?')
    pagination_class = PerPage100


class TranslationFeedbackViewsSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = TranslationFeedbackSecureSerializer


class ContactViewsSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = ContactSecureSerializer


class DownloadableViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = DownloadableSerializer
    queryset = Downloadable.objects.all().select_related('language').order_by('id')
    pagination_class = PerPage1000
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name', 'description']
    filterset_fields = ['language', 'language__name']

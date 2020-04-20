from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, viewsets, filters
from rest_framework.exceptions import ValidationError

from translateforsg.pagination import PerPage1000, PerPage100
from translations.models import Language, Phrase, Category, Translation, Contributor
from translations.serializers import PhraseSerializer, LanguageSerializer, CategorySerializer, \
    TranslationSerializerMain, ContributorSerializer


class PhraseViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = PhraseSerializer
    queryset = Phrase.objects.all() \
        .select_related('category') \
        .prefetch_related('translation_set', 'translation_set__language') \
        .order_by('id')
    pagination_class = PerPage1000
    filter_backends = [filters.SearchFilter]
    search_fields = ['summary', 'content']


class LanguageViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = LanguageSerializer
    queryset = Language.objects.all().order_by('name')
    pagination_class = PerPage1000


class CategoryViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.all().order_by('id')
    pagination_class = PerPage1000

    def get_queryset(self):
        qs = super().get_queryset()

        parents_only = self.request.query_params.get('parents_only')
        if parents_only:
            qs = qs.filter(parent_category__isnull=(parents_only == 'true'))

        return qs


class TranslationViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = TranslationSerializerMain
    queryset = Translation.objects.all() \
        .select_related('phrase', 'phrase__category') \
        .order_by('phrase_id')

    pagination_class = PerPage100
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['phrase__summary', 'phrase__content', 'content']
    filterset_fields = ['language__name', 'phrase__category__name', 'phrase__category']

    def list(self, request, *args, **kwargs):
        if not self.request.query_params.get('language__name'):
            raise ValidationError({'detail': 'Must provide language as a filter'})
        return super().list(request, *args, **kwargs)


class ContributorViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = ContributorSerializer
    queryset = Contributor.objects.all().order_by('?')
    pagination_class = PerPage1000

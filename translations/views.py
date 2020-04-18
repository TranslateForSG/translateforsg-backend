from rest_framework import mixins, viewsets, filters

from translateforsg.pagination import PerPage100
from translations.models import Language, Phrase, Category, Volunteer
from translations.serializers import PhraseSerializer, LanguageSerializer, CategorySerializer, VolunteerSerializer


class PhraseViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = PhraseSerializer
    queryset = Phrase.objects.all()
    pagination_class = PerPage100
    filter_backends = [filters.SearchFilter]
    search_fields = ['summary', 'content']


class LanguageViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = LanguageSerializer
    queryset = Language.objects.all().order_by('name')
    pagination_class = PerPage100


class CategoryViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.all().order_by('name')
    pagination_class = PerPage100


class VolunteerViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = VolunteerSerializer
    queryset = Volunteer.objects.all().order_by('?')  # make sure to randomly order
    pagination_class = PerPage100

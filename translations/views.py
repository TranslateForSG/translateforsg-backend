from rest_framework import mixins, viewsets, filters

from translateforsg.pagination import PerPage100
from translations.models import Language, Phrase, Category, Volunteer
from translations.serializers import PhraseSerializer, LanguageSerializer, CategorySerializer, VolunteerSerializer


class PhraseViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = PhraseSerializer
    queryset = Phrase.objects.all().order_by('id')
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

    def get_queryset(self):
        qs = super().get_queryset()

        parents_only = self.request.query_params.get('parents_only')
        if parents_only:
            qs = qs.filter(parent_category__isnull=(parents_only == 'true'))

        return qs


class VolunteerViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = VolunteerSerializer
    queryset = Volunteer.get_available_volunteers().order_by('?')  # make sure to randomly order
    pagination_class = PerPage100

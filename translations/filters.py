import django_filters

from translations.models import Translation


class TranslationFilterSet(django_filters.FilterSet):
    phrase__category__name = django_filters.CharFilter(field_name='phrase__categories__name', lookup_expr='iexact')

    class Meta:
        model = Translation
        fields = ['language__name', 'phrase__categories', 'phrase__categories__name']

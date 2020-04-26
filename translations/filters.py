import django_filters

from translations.models import Translation


class TranslationFilterSet(django_filters.FilterSet):
    phrase__category__name = django_filters.CharFilter(field_name='phrase__categories__name', lookup_expr='iexact')
    lookup = django_filters.CharFilter(field_name='phrase__content', lookup_expr='iexact')
    phrases = django_filters.CharFilter(method='filter_phrases')

    class Meta:
        model = Translation
        fields = ['language__name', 'phrase__categories', 'phrase__categories__name']

    def filter_phrases(self, queryset, name, value: str):
        try:
            ids = map(int, value.split(','))
            return queryset.filter(phrase_id__in=ids)
        except ValueError:
            return queryset

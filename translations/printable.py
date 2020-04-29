from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from translations.filters import TranslationFilterSet
from translations.models import Translation, Language


def print_category(request: HttpRequest) -> HttpResponse:
    qs = Translation.objects.all() \
        .select_related('phrase') \
        .prefetch_related('phrase__categories') \
        .order_by('phrase__categories__order', 'phrase__order')

    context = {
        'filter': TranslationFilterSet(data=request.GET, queryset=qs),
        'language': Language.objects.get(name=request.GET['language__name'])
    }

    return render(request, 'translations/print_list.html', context=context)

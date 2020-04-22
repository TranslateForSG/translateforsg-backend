from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.utils.translation import ugettext_lazy as _

from translations.models import Category, Phrase, PhraseCategory


class PhraseForm(forms.ModelForm):
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        widget=FilteredSelectMultiple(_('Category'), False, attrs={'rows': '10'}))

    def __init__(self, *args, **kwargs):
        if 'instance' in kwargs:
            initial = kwargs.setdefault('initial', {})
            if kwargs['instance']:
                initial['categories'] = [t.category.pk for t in kwargs['instance'].phrasecategory_set.all()]

        forms.ModelForm.__init__(self, *args, **kwargs)

    def save(self, commit=True):
        instance = forms.ModelForm.save(self, commit)

        old_save_m2m = self.save_m2m

        def save_m2m():
            old_save_m2m()

            categories = [s for s in self.cleaned_data['categories']]
            for phrase_category in instance.phrasecategory_set.all():
                if phrase_category.category not in categories:
                    phrase_category.delete()
                else:
                    categories.remove(phrase_category.category)

            for category in categories:
                PhraseCategory.objects.create(message=category, forum=instance)

        self.save_m2m = save_m2m

        return instance

    class Meta:
        model = Phrase
        fields = ['summary', 'content', 'categories']

from rest_framework import mixins, viewsets, serializers, filters

from translateforsg.pagination import PerPage100
from translations.models import Translation, Language, Phrase, Category


class TranslationSerializer(serializers.ModelSerializer):
    language = serializers.StringRelatedField()
    category = serializers.StringRelatedField()

    class Meta:
        model = Translation
        fields = ['language', 'category', 'content', 'special_note', 'audio_clip']


class PhraseSerializer(serializers.ModelSerializer):
    translations = TranslationSerializer(many=True, source='translation_set')

    class Meta:
        model = Phrase
        fields = ['summary', 'content', 'translations']


class PhraseViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = PhraseSerializer
    queryset = Phrase.objects.all()
    pagination_class = PerPage100
    filter_backends = [filters.SearchFilter]
    search_fields = ['summary', 'content']


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ['name', 'native_name', 'code']


class LanguageViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = LanguageSerializer
    queryset = Language.objects.all().order_by('name')
    pagination_class = PerPage100


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name']


class CategoryViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.all().order_by('name')
    pagination_class = PerPage100

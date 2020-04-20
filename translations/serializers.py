from rest_framework import serializers

from translations.models import Translation, Language, Phrase, Category, Contributor


class TranslationSerializer(serializers.ModelSerializer):
    language = serializers.StringRelatedField()
    category = serializers.StringRelatedField()

    class Meta:
        model = Translation
        fields = ['language', 'category', 'content', 'special_note', 'audio_clip']


class PhraseSerializerWithoutTranslation(serializers.ModelSerializer):
    category = serializers.StringRelatedField()

    class Meta:
        model = Phrase
        fields = ['summary', 'content', 'category']


class PhraseSerializer(serializers.ModelSerializer):
    translations = TranslationSerializer(many=True, source='translation_set')
    category = serializers.StringRelatedField()

    class Meta:
        model = Phrase
        fields = ['summary', 'content', 'category', 'translations']


class TranslationSerializerMain(serializers.ModelSerializer):
    language = serializers.StringRelatedField()
    category = serializers.StringRelatedField()
    phrase = PhraseSerializerWithoutTranslation()

    class Meta:
        model = Translation
        fields = ['language', 'category', 'content', 'special_note', 'audio_clip', 'phrase']


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ['name', 'native_name', 'code']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class ContributorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contributor
        fields = ['name']

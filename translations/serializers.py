from rest_framework import serializers

from translations.models import Translation, Language, Phrase, Category, Volunteer


class TranslationSerializer(serializers.ModelSerializer):
    language = serializers.StringRelatedField()
    category = serializers.StringRelatedField()

    class Meta:
        model = Translation
        fields = ['language', 'category', 'content', 'special_note', 'audio_clip']


class PhraseSerializer(serializers.ModelSerializer):
    translations = TranslationSerializer(many=True, source='translation_set')
    category = serializers.StringRelatedField()

    class Meta:
        model = Phrase
        fields = ['summary', 'content', 'category', 'translations']


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ['name', 'native_name', 'code']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class VolunteerSerializer(serializers.ModelSerializer):
    language = serializers.StringRelatedField()

    class Meta:
        model = Volunteer
        fields = ['display_name', 'language', 'phone_number', 'availability', 'ethnicity', 'notes']

from drf_recaptcha.fields import ReCaptchaV2Field
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from translations.models import Translation, Language, Phrase, Category, Contributor, UserType, TranslationFeedback


class TranslationSerializer(serializers.ModelSerializer):
    language = serializers.StringRelatedField()
    category = serializers.StringRelatedField()

    class Meta:
        model = Translation
        fields = ['language', 'category', 'content', 'special_note', 'audio_clip']


class PhraseSerializerWithoutTranslation(serializers.ModelSerializer):
    class Meta:
        model = Phrase
        fields = ['summary', 'content']


class PhraseSerializer(serializers.ModelSerializer):
    translations = TranslationSerializer(many=True, source='translation_set')

    class Meta:
        model = Phrase
        fields = ['summary', 'content', 'translations']


class TranslationSerializerMain(serializers.ModelSerializer):
    language = serializers.StringRelatedField()
    phrase = PhraseSerializerWithoutTranslation()

    class Meta:
        model = Translation
        fields = ['language', 'content', 'special_note', 'audio_clip', 'phrase']


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ['name', 'native_name', 'code']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'needs_original_phrase']


class ContributorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contributor
        fields = ['name']


class UserTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserType
        fields = ['name', 'needs_original_phrase']


class TranslationFeedbackSecureSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100, required=False)
    whats_wrong = serializers.CharField(max_length=1000, required=False)
    suggestion = serializers.CharField(max_length=1000, required=False)

    recaptcha = ReCaptchaV2Field()

    def validate(self, attrs):
        if not attrs['whats_wrong'] and not attrs['suggestion']:
            raise ValidationError({
                'whats_wrong': 'Either whats_wrong or suggestion is required.',
                'suggestion': 'Either whats_wrong or suggestion is required.',
            })
        return super().validate(attrs)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        if 'recaptcha' in validated_data:
            validated_data.pop('recaptcha')
        return TranslationFeedback.objects.create(**validated_data)
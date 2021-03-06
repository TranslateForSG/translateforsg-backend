from drf_recaptcha.fields import ReCaptchaV2Field
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from translations.models import Translation, Language, Phrase, Category, Contributor, UserType, TranslationFeedback, \
    Contact, Downloadable, Section


class TranslationSerializer(serializers.ModelSerializer):
    language = serializers.StringRelatedField()
    category = serializers.StringRelatedField()

    class Meta:
        model = Translation
        fields = ['id', 'language', 'category', 'content', 'romanized', 'special_note', 'audio_clip']


class PhraseSerializerWithoutTranslation(serializers.ModelSerializer):
    class Meta:
        model = Phrase
        fields = ['id', 'summary', 'content']


class PhraseSerializer(serializers.ModelSerializer):
    translations = TranslationSerializer(many=True, source='translation_set')

    class Meta:
        model = Phrase
        fields = ['id', 'summary', 'content', 'translations']


class TranslationSerializerMain(serializers.ModelSerializer):
    language = serializers.StringRelatedField()
    phrase = PhraseSerializerWithoutTranslation()

    class Meta:
        model = Translation
        fields = ['id', 'language', 'content', 'romanized', 'special_note', 'audio_clip', 'phrase']


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
    name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    whats_wrong = serializers.CharField(max_length=1000, required=False, allow_blank=True)
    suggestion = serializers.CharField(max_length=1000, required=False, allow_blank=True)
    translation_id = serializers.IntegerField(required=True)

    recaptcha = ReCaptchaV2Field()

    def validate(self, attrs):
        if not attrs.get('whats_wrong', '').strip() and not attrs.get('suggestion', '').strip():
            raise ValidationError({
                'whats_wrong': 'Either whats_wrong or suggestion is required.',
                'suggestion': 'Either whats_wrong or suggestion is required.',
            })

        if not Translation.objects.filter(pk=attrs['translation_id']).exists():
            raise ValidationError({
                'translation_id': 'Translation does not exist'
            })
        return super().validate(attrs)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        if 'recaptcha' in validated_data:
            validated_data.pop('recaptcha')
        return TranslationFeedback.objects.create(**validated_data)


class ContactSecureSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    content = serializers.CharField(max_length=2000)

    recaptcha = ReCaptchaV2Field()

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        if 'recaptcha' in validated_data:
            validated_data.pop('recaptcha')
        return Contact.objects.create(**validated_data)


class DownloadableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Downloadable
        fields = ['id', 'name', 'description', 'downloadable_file', 'created_at', 'updated_at']


class SectionSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True, source='category_set')

    class Meta:
        model = Section
        fields = ['id', 'name', 'categories']

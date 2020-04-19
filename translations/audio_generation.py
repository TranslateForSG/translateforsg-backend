from django.core.files.base import ContentFile
from google.cloud import texttospeech

client = texttospeech.TextToSpeechClient()


def preprocess_as_saml(text: str):
    text = f'<speak>{text}</speak>'

    return text \
        .replace('।', '। <break time="400ms"/>')


def generate_audio_file(text: str, language_code):
    # Set the text input to be synthesized
    ssml = preprocess_as_saml(text)
    synthesis_input = texttospeech.types.SynthesisInput(ssml=ssml)

    # Build the voice request, select the language code ("en-US") and the ssml
    # voice gender ("neutral")
    voice = texttospeech.types.VoiceSelectionParams(
        language_code=language_code,
        ssml_gender=texttospeech.enums.SsmlVoiceGender.FEMALE)

    # Select the type of audio file you want returned
    audio_config = texttospeech.types.AudioConfig(
        audio_encoding=texttospeech.enums.AudioEncoding.MP3,
        speaking_rate=0.85
    )

    # Perform the text-to-speech request on the text input with the selected
    # voice parameters and audio file type
    response = client.synthesize_speech(synthesis_input, voice, audio_config)

    return ContentFile(response.audio_content)

import gradio as gr #interface to record microphone audio
import assemblyai as aai #assembly api for getting transcript from audio
from translate import Translator #python tool for translating text
#from elevenlabs import VoiceSettings
#from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs import play
import uuid
from pathlib import Path

load_dotenv()

def voice_to_voice(audio_file):
    #transcribe audio
    transcription_response = audio_transcription(audio_file)

    if transcription_response.status == aai.TranscriptStatus.error:
        raise gr.Error(transcription_response.error)
    else:
        text = transcription_response.text #python sdk waits for this api call to complete

    es_translation, ru_translation, ja_translation = text_translation(text)

    es_audi_path = text_to_speech(es_translation)
    ru_audi_path = text_to_speech(ru_translation)
    ja_audi_path = text_to_speech(ja_translation)

    es_path = Path(es_audi_path)
    ru_path = Path(ru_audi_path)
    ja_path = Path(ja_audi_path)

    return es_path, ru_path, ja_path


def audio_transcription(audio_file):
    aai.settings.api_key = "5f7b181081ff481892b4ba7bd348d96d"

    transcriber = aai.Transcriber()
    transcription = transcriber.transcribe(audio_file)
    return transcription

def text_translation(text):
    translator_es = Translator(from_lang="en", to_lang="es")
    es_text = translator_es.translate(text)

    translator_ru = Translator(from_lang="en", to_lang="ru")
    ru_text = translator_ru.translate(text)

    translator_ja = Translator(from_lang="en", to_lang="ja")
    ja_text = translator_ja.translate(text)

    return es_text, ru_text, ja_text


def text_to_speech(text):
    client = ElevenLabs(
        api_key="sk_a8f1408cdfdac8a63d111a00f7c01b9b2f2e8f7cfc94568a"
    )
    audio = client.text_to_speech.convert(
        text=text,
        voice_id="xCT9WoUcBIC7qMxwWvm4",
        model_id="eleven_multilingual_v2",
        output_format="mp3_44100_128",
    )
    #return audio
    save_file_path = f"{uuid.uuid4()}.mp3"

    # Writing the audio to a file
    with open(save_file_path, "wb") as f:
        for chunk in audio:
            if chunk:
                f.write(chunk)

    print(f"{save_file_path}: A new audio file was saved successfully!")

    # Return the path of the saved audio file
    return save_file_path
   

audio_input = gr.Audio(
    sources=["microphone"], 
    type="filepath"
)

demo = gr.Interface(
    fn=voice_to_voice, 
    inputs=audio_input, 
    outputs=[gr.Audio(label="Spanish"), gr.Audio(label="Russian"), gr.Audio(label="Japanese")]
)

if __name__ == "__main__":
    demo.launch()
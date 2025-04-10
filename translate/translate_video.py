# translate/translate_video.py

import os
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from gtts import gTTS
from googletrans import Translator as GoogleTranslator
import whisper

# Ensure ffmpeg is in path
os.environ["PATH"] += os.pathsep + r"C:\Users\lenovo\Downloads\ffmpeg-7.1.1-essentials_build\ffmpeg\bin"

def process_video(input_path, output_dir):
    # Load video
    video = VideoFileClip(input_path)
    audio_path = os.path.join(output_dir, "extracted_audio.wav")
    video.audio.write_audiofile(audio_path)

    # Whisper Transcription
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    original_text = result["text"]

    # Translate
    translator = GoogleTranslator()
    translated = translator.translate(original_text, src='en', dest='hi').text

    # Text-to-speech
    tts_path = os.path.join(output_dir, "translated_audio.mp3")
    tts = gTTS(text=translated, lang='hi')
    tts.save(tts_path)

    # Merge new audio into video
    new_audio = AudioFileClip(tts_path)
    final_video = video.set_audio(new_audio)
    final_output_path = os.path.join(output_dir, "final_video.mp4")
    final_video.write_videofile(final_output_path, codec='libx264', audio_codec='aac')

    return final_output_path, original_text, translated

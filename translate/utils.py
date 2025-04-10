import os
import uuid
import moviepy.editor  as mp
from gtts import gTTS
import whisper

os.environ["PATH"] += os.pathsep + r"C:\Users\lenovo\Downloads\ffmpeg-7.1.1-essentials_build\ffmpeg\bin"

# ✅ Function to extract audio from a video file and save it as a separate audio file
def extract_audio_from_video(video_path, output_audio_path):
    # """
    # Extracts audio from a video file and saves it to the specified path.

    # Args:
    #     video_path (str): Path to the input video file.
    #     output_audio_path (str): Path to save the extracted audio (.wav or .mp3).
    # """
    try:
        video = mp.VideoFileClip(video_path)
        video.audio.write_audiofile(output_audio_path)
        print(f"Audio extracted to: {output_audio_path}")
    except Exception as e:
        print(f"Error extracting audio: {e}")

# ✅ Function to transcribe audio using OpenAI Whisper
def transcribe_audio(audio_path, language="en"):
    """
    Transcribes speech from an audio file using OpenAI's Whisper model.

    Args:
        audio_path (str): Path to the audio file.
        language (str): Language of the audio for better accuracy.

    Returns:
        str: Transcribed text.
    """
    try:
        model = whisper.load_model("base")  # You can use 'tiny', 'base', 'small', etc.
        result = model.transcribe(audio_path, language=language)
        return result['text']
    except Exception as e:
        print(f"Error transcribing audio: {e}")
        return ""

# ✅ Function to generate a speech (MP3 file) from input text
def generate_speech_file(text, lang='en'):
    """
    Converts input text into speech and saves it as an MP3 file.

    Args:
        text (str): Text to convert to speech.
        lang (str): Language code (e.g., 'en', 'hi', 'fr').

    Returns:
        str: Path to the generated MP3 file.
    """
    try:
        filename = f"{uuid.uuid4().hex}.mp3"
        filepath = os.path.join("media", "tts", filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        tts = gTTS(text=text, lang=lang)
        tts.save(filepath)
        return filepath
    except Exception as e:
        print(f"Error generating speech file: {e}")
        return ""

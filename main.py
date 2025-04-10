from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.VideoClip import TextClip
from moviepy.editor import concatenate_videoclips


from gtts import gTTS
from googletrans import Translator
import whisper

# Utilities
import os
os.environ["PATH"] += os.pathsep + r"C:\Users\lenovo\Downloads\ffmpeg-7.1.1-essentials_build\ffmpeg\bin"
# Step 1: Extract audio from video
video = VideoFileClip("input/input_video.mp4")
video.audio.write_audiofile("output/extracted_audio.wav")

# Step 2: Transcribe audio using Whisper
model = whisper.load_model("base")  # you can also try "small", "medium" for better accuracy
result = model.transcribe("output/extracted_audio.wav")
original_text = result["text"]
print("Original English Text:", original_text)

# Step 3: Translate text to Hindi
translator = Translator()
translated = translator.translate(original_text, src='en', dest='hi')
translated_text = translated.text
print("Translated Text:", translated_text)

# Step 4: Convert translated text to speech (Hindi)
tts = gTTS(text=translated_text, lang='hi')
tts.save("output/translated_audio.mp3")

# Step 5: Add translated audio back to video
new_audio = AudioFileClip("output/translated_audio.mp3")
final_video = video.set_audio(new_audio)
final_video.write_videofile("output/final_video.mp4", codec='libx264', audio_codec='aac')

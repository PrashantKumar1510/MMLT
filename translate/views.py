# views.py
import os
import uuid
import tempfile

from django.shortcuts import render
from django.http import JsonResponse, FileResponse
from django.conf import settings
from django.core.files.storage import FileSystemStorage

from rest_framework.decorators import api_view
from rest_framework.response import Response

from deep_translator import GoogleTranslator
from gtts import gTTS
from langdetect import detect
import whisper
from functools import lru_cache
from .translate_video import process_video
from .utils import extract_audio_from_video, transcribe_audio, generate_speech_file

# Add FFmpeg to system PATH for subprocess and whisper to work
os.environ["PATH"] += os.pathsep + r"C:\Users\lenovo\Downloads\ffmpeg-7.1.1-essentials_build\ffmpeg\bin"

@lru_cache()
def get_whisper_model():
    return whisper.load_model("base")


# ----------------- Web Page View: Home Page ----------------- #
def index(request):
    """
    Handle GET and POST for uploading a video and processing it for translation.
    """
    if request.method == 'POST' and request.FILES.get('video_file'):
        try:
            video_file = request.FILES['video_file']

            # Save file to /input folder
            fs = FileSystemStorage(location=os.path.join(settings.BASE_DIR, 'input'))
            filename = fs.save(video_file.name, video_file)
            input_path = fs.path(filename)

            output_dir = os.path.join(settings.BASE_DIR, 'output')
            final_video_path, original_text, translated_text = process_video(input_path, output_dir)

            return render(request, 'frontend/index.html', {
                'original': original_text,
                'translated': translated_text,
                'final_video': os.path.basename(final_video_path)
            })
        except Exception as e:
            return render(request, 'frontend/index.html', {'error': str(e)})

    return render(request, 'frontend/index.html')


# ----------------- API: Translate Text ----------------- #
@api_view(['GET', 'POST'])
def translate_text(request):
    """
    Translate a given text using Google Translate API.
    Accepts: text, source_lang, target_lang
    """
    if request.method == 'GET':
        return Response({"message": "Send a POST request with text, source_lang & target_lang"})

    text = request.data.get("text", "")
    source_lang = request.data.get("source_lang", "auto")
    target_lang = request.data.get("target_lang", "en")

    if not text:
        return Response({"error": "No text provided"}, status=400)

    try:
        translated_text = GoogleTranslator(source=source_lang, target=target_lang).translate(text)
        return Response({
            "input_text": text,
            "translated_text": translated_text,
            "source_language": source_lang,
            "target_language": target_lang
        })
    except Exception as e:
        return Response({"error": str(e)}, status=500)


# ----------------- API: Text to Speech ----------------- #
# views.py

@api_view(['POST'])
def text_to_speech(request):
    """
    Convert text to speech using gTTS.
    Accepts: text, lang
    Returns: MP3 audio file
    """
    text = request.data.get("text", "")
    lang = request.data.get("lang", "en")

    if not text:
        return JsonResponse({"error": "No text provided"}, status=400)

    try:
        filename = f"speech_{uuid.uuid4().hex}.mp3"
        filepath = os.path.join(settings.MEDIA_ROOT, filename)

        # Generate speech and save it to filepath
        generated_path = generate_speech_file(text, lang, filepath)

        if not os.path.exists(generated_path):
            return JsonResponse({"error": "Failed to generate speech file"}, status=500)

        return FileResponse(open(generated_path, "rb"), content_type="audio/mpeg")
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)



# ----------------- API: Transcribe Audio File ----------------- #
@api_view(['POST'])
def transcribe_audio_api(request):
    """
    Transcribe uploaded audio using Whisper.
    Accepts: audio_file (.wav/.mp3)
    """
    if request.FILES.get("audio_file"):
        audio_file = request.FILES["audio_file"]
        #save file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
            for chunk in audio_file.chunks():
                temp_audio.write(chunk)
            temp_audio_path = temp_audio.name

        try:
            model = get_whisper_model()
            result = model.transcribe(temp_audio_path)
            transcription = result["text"]
        except Exception as e:
            transcription = f"Error: {str(e)}"
        finally:
            os.remove(temp_audio_path)

        return JsonResponse({"transcription": transcription})

    return JsonResponse({"error": "Invalid request"}, status=400)


# ----------------- Web Page View: Simple Upload (No Processing) ----------------- #
def upload_video(request):
    """
    Just upload a video file and display it without processing.
    """
    if request.method == 'POST' and request.FILES.get('video'):
        video = request.FILES['video']
        fs = FileSystemStorage()
        filename = fs.save(video.name, video)
        video_url = fs.url(filename)
        return render(request, 'video_upload.html', {'video_url': video_url})

    return render(request, 'video_upload.html')


# ----------------- API: Upload + Transcribe Audio Only ----------------- #
def handle_uploaded_video(request):
    """
    Accepts a video file, extracts audio, transcribes it using Whisper.
    """
    if request.method == 'POST' and request.FILES.get('video'):
        video_file = request.FILES['video']
        filename = video_file.name
        video_path = os.path.join(settings.MEDIA_ROOT, filename)

        with open(video_path, 'wb+') as destination:
            for chunk in video_file.chunks():
                destination.write(chunk)

        audio_output_path = os.path.join(settings.MEDIA_ROOT, f"{os.path.splitext(filename)[0]}.wav")
        audio_file = extract_audio_from_video(video_path, audio_output_path)

        if audio_file:
            transcript_text = transcribe_audio(audio_file)
            if transcript_text:
                return JsonResponse({'transcription': transcript_text})
            return JsonResponse({'error': 'Transcription failed'}, status=500)
        return JsonResponse({'error': 'Audio extraction failed'}, status=500)

    return JsonResponse({'error': 'No video file provided'}, status=400)


# ----------------- Web Page View: Video to Translated Audio ----------------- #
def video_to_video_translation(request):
    """
    Full pipeline: Upload a video → Extract audio → Transcribe → Translate → Generate TTS audio
    Displays translated audio as downloadable.
    """
    if request.method == 'POST' and request.FILES.get('video'):
        video_file = request.FILES['video']
        filename = video_file.name
        video_path = os.path.join(settings.MEDIA_ROOT, filename)

        with open(video_path, 'wb+') as destination:
            for chunk in video_file.chunks():
                destination.write(chunk)

        audio_output_path = os.path.join(settings.MEDIA_ROOT, f"{os.path.splitext(filename)[0]}.wav")
        audio_file = extract_audio_from_video(video_path, audio_output_path)

        transcript_text = transcribe_audio(audio_file)
        translated_text = ""
        tts_output_path = ""

        try:
            source_lang = detect(transcript_text)
            target_lang = request.POST.get("target_lang", "hi")
            translated_text = GoogleTranslator(source=source_lang, target=target_lang).translate(transcript_text)

            tts_output_path = os.path.join(settings.MEDIA_ROOT, f"{os.path.splitext(filename)[0]}_translated.mp3")
            generate_speech_file(translated_text, target_lang, tts_output_path)

        except Exception as e:
            print("Translation or TTS failed:", e)

        return render(request, 'video_to_video_result.html', {
            'transcript': transcript_text,
            'translation': translated_text,
            'audio_path': tts_output_path.replace(settings.MEDIA_ROOT, '/media/')
        })

    return render(request, 'video_to_video_upload.html')

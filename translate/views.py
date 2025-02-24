from django.shortcuts import render
from deep_translator import GoogleTranslator
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['POST'])
def translate_text(request):
    data = request.data
    text = data.get("text", "")
    target_lang = data.get("target_lang", "en")  # Default: English

    if not text:
        return Response({"error": "No text provided"}, status=400)

    translated_text = GoogleTranslator(source="auto", target=target_lang).translate(text)

    return Response({
        "input_text": text,
        "translated_text": translated_text,
        "target_language": target_lang
    })



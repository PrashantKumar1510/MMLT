from django.urls import path
from .views import translate_text,text_to_speech
from django.conf import settings
from django.conf.urls.static import static
from . import views



urlpatterns = [
    path('', views.index, name='index'),
    path('translate/', translate_text, name='translate_text'),
    path("text_to_speech/", text_to_speech, name="text_to_speech"),
    path('api/transcribe_audio_api/', views.transcribe_audio, name='transcribe_audio_api'),
    path('upload-video/', views.upload_video, name='upload_video'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
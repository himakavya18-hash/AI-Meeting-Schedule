from django.urls import path
from transcripts.views import TranscriptUploadView, TranscriptDetailView

urlpatterns = [
    path('upload/', TranscriptUploadView.as_view(), name='transcript_upload'),
    path('<int:pk>/', TranscriptDetailView.as_view(), name='transcript_detail'),
]

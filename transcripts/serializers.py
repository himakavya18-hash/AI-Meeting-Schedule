from rest_framework import serializers
from transcripts.models import MeetingTranscript
from accounts.serializers import UserSerializer

class MeetingTranscriptSerializer(serializers.ModelSerializer):
    uploaded_by = UserSerializer(read_only=True)

    class Meta:
        model = MeetingTranscript
        fields = ['id', 'meeting', 'title', 'file', 'raw_text', 'uploaded_by', 'created_at']

from django.db import models
from django.conf import settings
from meetings.models import Meeting

class MeetingTranscript(models.Model):
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name='transcripts')
    title = models.CharField(max_length=255, blank=True, null=True)
    file = models.FileField(upload_to='transcripts/', blank=True, null=True)
    raw_text = models.TextField()
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Transcript for {self.meeting.title} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"

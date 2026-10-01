from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from meetings.models import Meeting
from transcripts.models import MeetingTranscript
from transcripts.serializers import MeetingTranscriptSerializer
from transcripts.parsers import extract_transcript_text

class TranscriptUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        meeting_id = request.data.get('meeting_id')
        raw_text = request.data.get('raw_text', '').strip()
        uploaded_file = request.FILES.get('file')

        if not meeting_id:
            return Response({'error': 'meeting_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            meeting = Meeting.objects.get(pk=meeting_id, meeting_participants__user=request.user)
        except Meeting.DoesNotExist:
            return Response({'error': 'Meeting not found or access denied'}, status=status.HTTP_404_NOT_FOUND)

        extracted_text = ""
        if uploaded_file:
            try:
                extracted_text = extract_transcript_text(uploaded_file)
            except ValueError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        final_text = (extracted_text + "\n\n" + raw_text).strip()
        if not final_text:
            return Response({'error': 'Please provide a file or direct transcript text'}, status=status.HTTP_400_BAD_REQUEST)

        transcript = MeetingTranscript.objects.create(
            meeting=meeting,
            title=f"Transcript - {meeting.title}",
            file=uploaded_file,
            raw_text=final_text,
            uploaded_by=request.user
        )

        # Mark meeting status as Completed if desired
        meeting.status = 'Completed'
        meeting.save(update_fields=['status'])

        return Response({
            'message': 'Transcript uploaded successfully',
            'transcript': MeetingTranscriptSerializer(transcript).data
        }, status=status.HTTP_201_CREATED)

class TranscriptDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            transcript = MeetingTranscript.objects.get(pk=pk, meeting__meeting_participants__user=request.user)
            return Response(MeetingTranscriptSerializer(transcript).data)
        except MeetingTranscript.DoesNotExist:
            return Response({'error': 'Transcript not found or access denied'}, status=status.HTTP_404_NOT_FOUND)

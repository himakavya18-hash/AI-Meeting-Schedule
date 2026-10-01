from datetime import datetime
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from meetings.models import Meeting, MeetingParticipant
from meetings.serializers import MeetingSerializer
from meetings.services import check_participants_availability, suggest_alternative_time_slots
from notifications.services import notify_meeting_created

User = get_user_model()

class MeetingListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = Meeting.objects.filter(
            meeting_participants__user=request.user
        ).distinct().order_by('-date', '-start_time')

        # Filters
        date_str = request.query_params.get('date')
        status_param = request.query_params.get('status')
        meeting_type = request.query_params.get('meeting_type')
        department = request.query_params.get('department')
        participant_id = request.query_params.get('participant_id')

        if date_str:
            queryset = queryset.filter(date=date_str)
        if status_param:
            queryset = queryset.filter(status=status_param)
        if meeting_type:
            queryset = queryset.filter(meeting_type=meeting_type)
        if department:
            queryset = queryset.filter(organizer__department=department)
        if participant_id:
            queryset = queryset.filter(meeting_participants__user_id=participant_id)

        serializer = MeetingSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = MeetingSerializer(data=request.data)
        if serializer.is_valid():
            meeting = serializer.save(organizer=request.user)
            
            # Check availability for selected participants
            participants = list(meeting.participants.all())
            avail_res = check_participants_availability(
                participants, meeting.date, meeting.start_time, meeting.end_time, exclude_meeting_id=meeting.id
            )
            
            alt_slots = []
            if not avail_res['all_available']:
                alt_slots = suggest_alternative_time_slots(
                    participants, meeting.date, meeting.start_time, meeting.end_time, exclude_meeting_id=meeting.id
                )
                
            # Send notifications & emails
            notify_meeting_created(meeting, avail_res['available_users'], avail_res['unavailable_users'], alt_slots)

            return Response({
                'meeting': MeetingSerializer(meeting).data,
                'availability_report': {
                    'all_available': avail_res['all_available'],
                    'message': avail_res['message'],
                    'statuses': avail_res['statuses'],
                    'alternative_slots': alt_slots
                }
            }, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MeetingDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        try:
            return Meeting.objects.get(pk=pk, meeting_participants__user=user)
        except Meeting.DoesNotExist:
            return None

    def get(self, request, pk):
        meeting = self.get_object(pk, request.user)
        if not meeting:
            return Response({'error': 'Meeting not found or access denied'}, status=status.HTTP_404_NOT_FOUND)
        serializer = MeetingSerializer(meeting)
        return Response(serializer.data)

    def put(self, request, pk):
        meeting = self.get_object(pk, request.user)
        if not meeting:
            return Response({'error': 'Meeting not found or access denied'}, status=status.HTTP_404_NOT_FOUND)
            
        if meeting.organizer != request.user:
            return Response({'error': 'Only the organizer can edit this meeting'}, status=status.HTTP_403_FORBIDDEN)

        serializer = MeetingSerializer(meeting, data=request.data, partial=True)
        if serializer.is_valid():
            meeting = serializer.save()
            return Response(MeetingSerializer(meeting).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        meeting = self.get_object(pk, request.user)
        if not meeting:
            return Response({'error': 'Meeting not found or access denied'}, status=status.HTTP_404_NOT_FOUND)
            
        if meeting.organizer != request.user:
            return Response({'error': 'Only the organizer can delete this meeting'}, status=status.HTTP_403_FORBIDDEN)

        meeting.delete()
        return Response({'message': 'Meeting deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

class CheckAvailabilityView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk=None):
        data = request.data
        participant_ids = data.get('participant_ids', [])
        date_str = data.get('date')
        start_str = data.get('start_time')
        end_str = data.get('end_time')

        if pk:
            try:
                meeting = Meeting.objects.get(pk=pk)
                participant_ids = list(meeting.participants.values_list('id', flat=True))
                date_str = str(meeting.date)
                start_str = str(meeting.start_time)
                end_str = str(meeting.end_time)
            except Meeting.DoesNotExist:
                return Response({'error': 'Meeting not found'}, status=status.HTTP_404_NOT_FOUND)

        if not (participant_ids and date_str and start_str and end_str):
            return Response({'error': 'participant_ids, date, start_time, and end_time are required'}, status=status.HTTP_400_BAD_REQUEST)

        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        start_time = datetime.strptime(start_str, '%H:%M' if len(start_str)==5 else '%H:%M:%S').time()
        end_time = datetime.strptime(end_str, '%H:%M' if len(end_str)==5 else '%H:%M:%S').time()

        users = User.objects.filter(id__in=participant_ids)
        avail_res = check_participants_availability(users, target_date, start_time, end_time, exclude_meeting_id=pk)

        alt_slots = []
        if not avail_res['all_available']:
            alt_slots = suggest_alternative_time_slots(users, target_date, start_time, end_time, exclude_meeting_id=pk)

        return Response({
            'all_available': avail_res['all_available'],
            'message': avail_res['message'],
            'available_count': avail_res['available_count'],
            'unavailable_count': avail_res['unavailable_count'],
            'total_count': avail_res['total_count'],
            'statuses': avail_res['statuses'],
            'alternative_slots': alt_slots
        })

class RespondToMeetingView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        response_status = request.data.get('response_status') # Accepted, Declined, Maybe
        response_note = request.data.get('response_note', '')

        if response_status not in ['Accepted', 'Declined', 'Maybe']:
            return Response({'error': 'Invalid response_status'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            participant = MeetingParticipant.objects.get(meeting_id=pk, user=request.user)
            participant.response_status = response_status
            participant.response_note = response_note
            participant.save()

            # Update overall meeting status
            meeting = participant.meeting
            meeting.update_auto_status()

            return Response({
                'message': f'Response updated to {response_status}',
                'meeting': MeetingSerializer(meeting).data
            })
        except MeetingParticipant.DoesNotExist:
            return Response({'error': 'You are not invited to this meeting'}, status=status.HTTP_403_FORBIDDEN)

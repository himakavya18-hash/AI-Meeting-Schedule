from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from meetings.models import Meeting
from transcripts.models import MeetingTranscript
from actions.models import Decision, ActionItem, UnresolvedQuestion, Dependency
from actions.serializers import (
    DecisionSerializer, ActionItemSerializer,
    UnresolvedQuestionSerializer, DependencySerializer
)
from ai_extractor.services import process_transcript_and_save_analysis

class ActionRegisterView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = ActionItem.objects.all().order_by('-created_at')

        # Filters
        owner = request.query_params.get('owner')
        status_param = request.query_params.get('status')
        priority = request.query_params.get('priority')
        meeting_id = request.query_params.get('meeting_id')

        if owner:
            queryset = queryset.filter(owner_name__icontains=owner)
        if status_param:
            queryset = queryset.filter(status=status_param)
        if priority:
            queryset = queryset.filter(priority=priority)
        if meeting_id:
            queryset = queryset.filter(meeting_id=meeting_id)

        serializer = ActionItemSerializer(queryset, many=True)
        return Response(serializer.data)

class MyActionItemsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        # Match assigned owner_user OR owner_name containing user's name
        actions = ActionItem.objects.filter(
            owner_user=user
        ) | ActionItem.objects.filter(
            owner_name__icontains=user.first_name if user.first_name else user.username
        )
        actions = actions.distinct().order_by('-created_at')
        
        serializer = ActionItemSerializer(actions, many=True)
        return Response(serializer.data)

class ActionDetailUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        try:
            action = ActionItem.objects.get(pk=pk)
        except ActionItem.DoesNotExist:
            return Response({'error': 'Action item not found'}, status=status.HTTP_404_NOT_FOUND)

        new_status = request.data.get('status')
        if new_status in ['Pending', 'In Progress', 'Completed', 'Overdue']:
            action.status = new_status
            action.save()

        if 'priority' in request.data:
            action.priority = request.data['priority']
            action.save()

        return Response(ActionItemSerializer(action).data)

class TriggerAIAnalysisView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, transcript_id):
        try:
            transcript = MeetingTranscript.objects.get(pk=transcript_id, meeting__meeting_participants__user=request.user)
        except MeetingTranscript.DoesNotExist:
            return Response({'error': 'Transcript not found or access denied'}, status=status.HTTP_404_NOT_FOUND)

        result = process_transcript_and_save_analysis(transcript)
        return Response({
            'message': 'AI Analysis completed successfully',
            'analysis': result
        }, status=status.HTTP_200_OK)

class MeetingAnalysisReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            meeting = Meeting.objects.get(pk=pk, meeting_participants__user=request.user)
        except Meeting.DoesNotExist:
            return Response({'error': 'Meeting not found or access denied'}, status=status.HTTP_404_NOT_FOUND)

        decisions = Decision.objects.filter(meeting=meeting)
        actions = ActionItem.objects.filter(meeting=meeting)
        questions = UnresolvedQuestion.objects.filter(meeting=meeting)
        dependencies = Dependency.objects.filter(meeting=meeting)
        transcript = MeetingTranscript.objects.filter(meeting=meeting).first()

        return Response({
            'meeting_id': meeting.id,
            'title': meeting.title,
            'date': meeting.date,
            'organizer': meeting.organizer.get_full_name() or meeting.organizer.username,
            'transcript_available': transcript is not None,
            'raw_transcript': transcript.raw_text if transcript else None,
            'decisions': DecisionSerializer(decisions, many=True).data,
            'action_items': ActionItemSerializer(actions, many=True).data,
            'unresolved_questions': UnresolvedQuestionSerializer(questions, many=True).data,
            'dependencies': DependencySerializer(dependencies, many=True).data,
        })

class UnresolvedQuestionsListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        questions = UnresolvedQuestion.objects.all().order_by('-created_at')
        return Response(UnresolvedQuestionSerializer(questions, many=True).data)

    def put(self, request, pk):
        try:
            q = UnresolvedQuestion.objects.get(pk=pk)
        except UnresolvedQuestion.DoesNotExist:
            return Response({'error': 'Question not found'}, status=status.HTTP_404_NOT_FOUND)

        status_val = request.data.get('status')
        if status_val in ['Unresolved', 'Resolved']:
            q.status = status_val
            if status_val == 'Resolved':
                q.resolved_by = request.user
            q.save()
            
        if 'resolution_notes' in request.data:
            q.resolution_notes = request.data['resolution_notes']
            q.save()

        return Response(UnresolvedQuestionSerializer(q).data)

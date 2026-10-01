from rest_framework import serializers
from actions.models import Decision, ActionItem, UnresolvedQuestion, Dependency
from accounts.serializers import UserSerializer
from meetings.serializers import MeetingSerializer

class DecisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Decision
        fields = ['id', 'meeting', 'decision', 'evidence', 'confidence', 'created_at']

class ActionItemSerializer(serializers.ModelSerializer):
    owner_user = UserSerializer(read_only=True)
    meeting_title = serializers.CharField(source='meeting.title', read_only=True)

    class Meta:
        model = ActionItem
        fields = [
            'id', 'meeting', 'meeting_title', 'task', 'owner_name', 'owner_user',
            'deadline', 'priority', 'evidence', 'status', 'created_at', 'updated_at'
        ]

class UnresolvedQuestionSerializer(serializers.ModelSerializer):
    resolved_by = UserSerializer(read_only=True)

    class Meta:
        model = UnresolvedQuestion
        fields = ['id', 'meeting', 'question', 'status', 'resolved_by', 'resolution_notes', 'created_at']

class DependencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Dependency
        fields = ['id', 'meeting', 'description', 'created_at']

from rest_framework import serializers
from django.contrib.auth import get_user_model
from meetings.models import Meeting, MeetingParticipant, MeetingInvitation
from accounts.serializers import UserSerializer

User = get_user_model()

class MeetingParticipantSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='user', write_only=True
    )

    class Meta:
        model = MeetingParticipant
        fields = ['id', 'user', 'user_id', 'response_status', 'response_note', 'updated_at']

class MeetingSerializer(serializers.ModelSerializer):
    organizer = UserSerializer(read_only=True)
    meeting_participants = MeetingParticipantSerializer(many=True, read_only=True)
    participant_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )
    duration_minutes = serializers.SerializerMethodField()

    class Meta:
        model = Meeting
        fields = [
            'id', 'title', 'description', 'organizer', 'meeting_type', 'priority',
            'date', 'start_time', 'end_time', 'agenda', 'status',
            'meeting_participants', 'participant_ids', 'duration_minutes',
            'created_at', 'updated_at'
        ]

    def get_duration_minutes(self, obj):
        if obj.start_time and obj.end_time:
            dummy_date = obj.date
            from datetime import datetime
            t1 = datetime.combine(dummy_date, obj.start_time)
            t2 = datetime.combine(dummy_date, obj.end_time)
            return int((t2 - t1).total_seconds() / 60)
        return 0

    def create(self, validated_data):
        participant_ids = validated_data.pop('participant_ids', [])
        meeting = Meeting.objects.create(**validated_data)
        
        # Add organizer as accepted participant
        MeetingParticipant.objects.create(
            meeting=meeting,
            user=meeting.organizer,
            response_status='Accepted'
        )
        
        # Add other participants as pending
        for p_id in participant_ids:
            if p_id != meeting.organizer.id:
                try:
                    u = User.objects.get(pk=p_id)
                    MeetingParticipant.objects.get_or_create(
                        meeting=meeting,
                        user=u,
                        defaults={'response_status': 'Pending'}
                    )
                except User.DoesNotExist:
                    pass
                    
        return meeting

    def update(self, instance, validated_data):
        participant_ids = validated_data.pop('participant_ids', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if participant_ids is not None:
            # Keep organizer
            existing = set(instance.meeting_participants.values_list('user_id', flat=True))
            new_ids = set(participant_ids) | {instance.organizer.id}
            
            # Remove removed
            instance.meeting_participants.exclude(user_id__in=new_ids).delete()
            # Add added
            for p_id in new_ids - existing:
                try:
                    u = User.objects.get(pk=p_id)
                    MeetingParticipant.objects.create(
                        meeting=instance,
                        user=u,
                        response_status='Accepted' if p_id == instance.organizer.id else 'Pending'
                    )
                except User.DoesNotExist:
                    pass
        return instance

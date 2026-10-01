from rest_framework import serializers
from django.contrib.auth import get_user_model
from accounts.models import Availability

User = get_user_model()

class AvailabilitySerializer(serializers.ModelSerializer):
    day_name = serializers.CharField(source='get_day_of_week_display', read_only=True)

    class Meta:
        model = Availability
        fields = ['id', 'day_of_week', 'day_name', 'start_time', 'end_time', 'is_available']

class UserSerializer(serializers.ModelSerializer):
    weekly_availabilities = AvailabilitySerializer(many=True, read_only=True)
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'employee_id', 'department', 'job_role', 'avatar_url', 'time_zone',
            'status', 'work_start_time', 'work_end_time', 'weekly_availabilities'
        ]

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username

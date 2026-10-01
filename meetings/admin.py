from django.contrib import admin
from meetings.models import Meeting, MeetingParticipant, MeetingInvitation

class MeetingParticipantInline(admin.TabularInline):
    model = MeetingParticipant
    extra = 1

@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ['title', 'organizer', 'meeting_type', 'priority', 'date', 'start_time', 'end_time', 'status']
    list_filter = ['meeting_type', 'priority', 'status', 'date']
    search_fields = ['title', 'description', 'agenda']
    inlines = [MeetingParticipantInline]

@admin.register(MeetingParticipant)
class MeetingParticipantAdmin(admin.ModelAdmin):
    list_display = ['meeting', 'user', 'response_status', 'updated_at']
    list_filter = ['response_status']

@admin.register(MeetingInvitation)
class MeetingInvitationAdmin(admin.ModelAdmin):
    list_display = ['meeting', 'invited_user', 'sent_at']

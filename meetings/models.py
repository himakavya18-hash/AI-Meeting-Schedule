from django.db import models
from django.conf import settings

class Meeting(models.Model):
    MEETING_TYPES = [
        ('Team Meeting', 'Team Meeting'),
        ('Client Meeting', 'Client Meeting'),
        ('Project Meeting', 'Project Meeting'),
        ('Review Meeting', 'Review Meeting'),
        ('Planning Meeting', 'Planning Meeting'),
        ('Other', 'Other'),
    ]

    PRIORITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
        ('Urgent', 'Urgent'),
    ]

    STATUS_CHOICES = [
        ('Draft', 'Draft'),
        ('Pending Confirmation', 'Pending Confirmation'),
        ('Scheduled', 'Scheduled'),
        ('Partially Confirmed', 'Partially Confirmed'),
        ('Cancelled', 'Cancelled'),
        ('Completed', 'Completed'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    organizer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='organized_meetings')
    meeting_type = models.CharField(max_length=50, choices=MEETING_TYPES, default='Team Meeting')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='Medium')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    agenda = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Scheduled')
    
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='MeetingParticipant',
        related_name='attended_meetings'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-start_time']

    def __str__(self):
        return f"{self.title} ({self.date} {self.start_time}-{self.end_time})"

    def update_auto_status(self):
        """
        Automatically updates meeting status based on participant responses.
        """
        if self.status in ['Cancelled', 'Completed']:
            return self.status
            
        participant_objs = self.meeting_participants.all()
        if not participant_objs.exists():
            return self.status
            
        responses = [p.response_status for p in participant_objs]
        if all(r == 'Accepted' for r in responses):
            self.status = 'Scheduled'
        elif any(r == 'Accepted' for r in responses):
            self.status = 'Partially Confirmed'
        elif all(r == 'Declined' for r in responses):
            self.status = 'Cancelled'
        else:
            self.status = 'Pending Confirmation'
            
        self.save(update_fields=['status'])
        return self.status

class MeetingParticipant(models.Model):
    RESPONSE_CHOICES = [
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Declined', 'Declined'),
        ('Maybe', 'Maybe'),
    ]

    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name='meeting_participants')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    response_status = models.CharField(max_length=20, choices=RESPONSE_CHOICES, default='Pending')
    response_note = models.TextField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('meeting', 'user')

    def __str__(self):
        return f"{self.user.username} - {self.meeting.title}: {self.response_status}"

class MeetingInvitation(models.Model):
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name='invitations')
    invited_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Invitation for {self.invited_user.username} to {self.meeting.title}"

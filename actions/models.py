from django.db import models
from django.conf import settings
from meetings.models import Meeting

class Decision(models.Model):
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name='decisions')
    decision = models.TextField()
    evidence = models.TextField(blank=True, null=True)
    confidence = models.FloatField(default=0.95)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Decision: {self.decision[:50]}"

class ActionItem(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('Overdue', 'Overdue'),
    ]

    PRIORITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
        ('Urgent', 'Urgent'),
    ]

    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name='action_items')
    task = models.TextField()
    owner_name = models.CharField(max_length=150, default='Not specified')
    owner_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_actions')
    deadline = models.CharField(max_length=100, default='Not specified')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='Medium')
    evidence = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Action ({self.owner_name}): {self.task[:40]}"

class UnresolvedQuestion(models.Model):
    STATUS_CHOICES = [
        ('Unresolved', 'Unresolved'),
        ('Resolved', 'Resolved'),
    ]

    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name='unresolved_questions')
    question = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Unresolved')
    resolved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    resolution_notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Question: {self.question[:50]} ({self.status})"

class Dependency(models.Model):
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name='dependencies')
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Dependency: {self.description[:50]}"

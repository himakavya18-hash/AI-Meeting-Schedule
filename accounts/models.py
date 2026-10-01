from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    firebase_uid = models.CharField(max_length=128, unique=True, blank=True, null=True)
    employee_id = models.CharField(max_length=50, unique=True, blank=True, null=True)
    department = models.CharField(max_length=100, default='Engineering')
    job_role = models.CharField(max_length=100, default='Software Engineer')
    avatar_url = models.URLField(max_length=500, blank=True, null=True)
    time_zone = models.CharField(max_length=50, default='UTC')
    
    # Global availability status: Available, Busy, On Leave
    AVAILABILITY_CHOICES = [
        ('Available', 'Available'),
        ('Busy', 'Busy'),
        ('On Leave', 'On Leave'),
    ]
    status = models.CharField(max_length=20, choices=AVAILABILITY_CHOICES, default='Available')
    
    # Default daily working hours
    work_start_time = models.TimeField(default='09:00:00')
    work_end_time = models.TimeField(default='17:00:00')

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.email})"

class Availability(models.Model):
    DAY_CHOICES = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='weekly_availabilities')
    day_of_week = models.IntegerField(choices=DAY_CHOICES)
    start_time = models.TimeField(default='09:00:00')
    end_time = models.TimeField(default='17:00:00')
    is_available = models.BooleanField(default=True)

    class Meta:
        unique_together = ('user', 'day_of_week')

    def __str__(self):
        day_name = dict(self.DAY_CHOICES).get(self.day_of_week, str(self.day_of_week))
        status_str = "Available" if self.is_available else "Unavailable"
        return f"{self.user.username} - {day_name}: {self.start_time}-{self.end_time} ({status_str})"

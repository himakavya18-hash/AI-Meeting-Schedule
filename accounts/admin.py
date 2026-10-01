from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from accounts.models import User, Availability

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Company Details', {'fields': ('firebase_uid', 'employee_id', 'department', 'job_role', 'avatar_url', 'time_zone', 'status', 'work_start_time', 'work_end_time')}),
    )
    list_display = ['username', 'email', 'first_name', 'last_name', 'department', 'job_role', 'status']

@admin.register(Availability)
class AvailabilityAdmin(admin.ModelAdmin):
    list_display = ['user', 'day_of_week', 'start_time', 'end_time', 'is_available']

from django.urls import path
from meetings.views import (
    MeetingListCreateView, MeetingDetailView,
    CheckAvailabilityView, RespondToMeetingView
)

urlpatterns = [
    path('', MeetingListCreateView.as_view(), name='meeting_list_create'),
    path('<int:pk>/', MeetingDetailView.as_view(), name='meeting_detail'),
    path('check-availability/', CheckAvailabilityView.as_view(), name='check_availability_global'),
    path('<int:pk>/check-availability/', CheckAvailabilityView.as_view(), name='check_availability_meeting'),
    path('<int:pk>/respond/', RespondToMeetingView.as_view(), name='respond_meeting'),
]

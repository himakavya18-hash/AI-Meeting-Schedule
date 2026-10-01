from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render, redirect

from django.contrib.auth.decorators import login_required

# Web Page Views
def home_page(request):
    return render(request, 'login.html')

def login_page(request):
    return render(request, 'login.html')

@login_required(login_url='/login/')
def dashboard_page(request):
    return render(request, 'dashboard.html')

@login_required(login_url='/login/')
def profile_page(request):
    return render(request, 'profile.html')

@login_required(login_url='/login/')
def create_meeting_page(request):
    return render(request, 'create_meeting.html')

@login_required(login_url='/login/')
def calendar_page(request):
    return render(request, 'calendar.html')

@login_required(login_url='/login/')
def meeting_detail_page(request, pk):
    return render(request, 'meeting_detail.html', {'meeting_id': pk})

@login_required(login_url='/login/')
def availability_page(request):
    return render(request, 'availability.html')

@login_required(login_url='/login/')
def invitations_page(request):
    return render(request, 'invitations.html')

@login_required(login_url='/login/')
def transcript_upload_page(request):
    return render(request, 'transcript_upload.html')

@login_required(login_url='/login/')
def ai_analysis_page(request, pk):
    return render(request, 'ai_analysis.html', {'meeting_id': pk})

@login_required(login_url='/login/')
def action_register_page(request):
    return render(request, 'action_register.html')

@login_required(login_url='/login/')
def my_actions_page(request):
    return render(request, 'my_actions.html')

@login_required(login_url='/login/')
def unresolved_questions_page(request):
    return render(request, 'unresolved_questions.html')

@login_required(login_url='/login/')
def notifications_page(request):
    return render(request, 'notifications.html')

@login_required(login_url='/login/')
def settings_page(request):
    return render(request, 'settings.html')

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API Endpoints
    path('api/accounts/', include('accounts.urls')),
    path('api/meetings/', include('meetings.urls')),
    path('api/transcripts/', include('transcripts.urls')),
    path('api/actions/', include('actions.urls')),
    path('api/notifications/', include('notifications.urls')),
    
    # Frontend Pages
    path('', home_page, name='home'),
    path('login/', login_page, name='login_page'),
    path('dashboard/', dashboard_page, name='dashboard_page'),
    path('profile/', profile_page, name='profile_page'),
    path('meetings/create/', create_meeting_page, name='create_meeting_page'),
    path('calendar/', calendar_page, name='calendar_page'),
    path('meetings/<int:pk>/', meeting_detail_page, name='meeting_detail_page'),
    path('availability/', availability_page, name='availability_page'),
    path('invitations/', invitations_page, name='invitations_page'),
    path('transcripts/upload/', transcript_upload_page, name='transcript_upload_page'),
    path('meetings/<int:pk>/ai-analysis/', ai_analysis_page, name='ai_analysis_page'),
    path('actions/', action_register_page, name='action_register_page'),
    path('actions/my/', my_actions_page, name='my_actions_page'),
    path('questions/', unresolved_questions_page, name='unresolved_questions_page'),
    path('notifications/', notifications_page, name='notifications_page'),
    path('settings/', settings_page, name='settings_page'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])

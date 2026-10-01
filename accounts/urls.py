from django.urls import path
from accounts.views import (
    EmailPasswordLoginView, RegisterView,
    FirebaseLoginView, DemoLoginView, LogoutView,
    CurrentUserProfileView, UserListView, AvailabilityUpdateView
)

urlpatterns = [
    path('login/', EmailPasswordLoginView.as_view(), name='api_email_login'),
    path('register/', RegisterView.as_view(), name='api_register'),
    path('firebase-login/', FirebaseLoginView.as_view(), name='firebase_login'),
    path('demo-login/', DemoLoginView.as_view(), name='demo_login'),
    path('logout/', LogoutView.as_view(), name='api_logout'),
    path('me/', CurrentUserProfileView.as_view(), name='user_profile'),
    path('users/', UserListView.as_view(), name='user_list'),
    path('availability/', AvailabilityUpdateView.as_view(), name='user_availability'),
]

from django.urls import path
from notifications.views import NotificationListView, MarkNotificationReadView

urlpatterns = [
    path('', NotificationListView.as_view(), name='notification_list'),
    path('<int:pk>/read/', MarkNotificationReadView.as_view(), name='mark_notification_read'),
    path('read-all/', MarkNotificationReadView.as_view(), name='mark_all_notifications_read'),
]

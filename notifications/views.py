from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from notifications.models import Notification
from notifications.serializers import NotificationSerializer

class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        notifications = Notification.objects.filter(user=request.user)
        serializer = NotificationSerializer(notifications, many=True)
        unread_count = notifications.filter(is_read=False).count()
        return Response({
            'unread_count': unread_count,
            'notifications': serializer.data
        })

class MarkNotificationReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk=None):
        if pk:
            try:
                notif = Notification.objects.get(pk=pk, user=request.user)
                notif.is_read = True
                notif.save()
            except Notification.DoesNotExist:
                return Response({'error': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
            
        return Response({'message': 'Notifications marked as read'})

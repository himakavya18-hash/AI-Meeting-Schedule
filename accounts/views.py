from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model, login, logout
from accounts.models import Availability
from accounts.serializers import UserSerializer, AvailabilitySerializer
from accounts.services import verify_firebase_id_token

User = get_user_model()

class EmailPasswordLoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        identifier = request.data.get('email', '').strip() or request.data.get('username', '').strip()
        password = request.data.get('password', '')

        if not identifier or not password:
            return Response({'error': 'Email/Username and password are required'}, status=status.HTTP_400_BAD_REQUEST)

        # Find user by email or username (case-insensitive)
        user = User.objects.filter(email__iexact=identifier).first()
        if not user:
            user = User.objects.filter(username__iexact=identifier).first()

        if not user or not user.check_password(password):
            return Response({'error': 'Invalid email/username or password.'}, status=status.HTTP_400_BAD_REQUEST)

        if not user.is_active:
            return Response({'error': 'This user account is inactive.'}, status=status.HTTP_403_FORBIDDEN)

        login(request, user)
        serializer = UserSerializer(user)
        return Response({
            'message': 'Login successful',
            'user': serializer.data
        })

class RegisterView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        import re
        email = request.data.get('email', '').strip().lower()
        password = request.data.get('password', '')
        first_name = request.data.get('first_name', '').strip()
        last_name = request.data.get('last_name', '').strip()
        username = request.data.get('username', '').strip() or email.split('@')[0]
        department = request.data.get('department', 'Engineering').strip()
        job_role = request.data.get('job_role', 'Team Member').strip()

        if not email or not password or not first_name:
            return Response({'error': 'First name, email, and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

        if len(password) < 6:
            return Response({'error': 'Password must be at least 6 characters long.'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email__iexact=email).exists():
            return Response({'error': f'An account with email {email} already exists. Please sign in.'}, status=status.HTTP_400_BAD_REQUEST)

        # Sanitize username
        clean_username = re.sub(r'[^\w.@+-]', '_', username)
        if not clean_username:
            clean_username = f"user_{User.objects.count()+1}"

        base_username = clean_username
        username = base_username
        counter = 1
        while User.objects.filter(username__iexact=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        employee_id = f"EMP-{User.objects.count()+1:04d}"

        try:
            user = User.objects.create(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                department=department or 'Engineering',
                job_role=job_role or 'Team Member',
                employee_id=employee_id
            )
            user.set_password(password)
            user.save()

            # Seed default Mon-Fri 9am-5pm availability
            from datetime import time
            for day in range(5):
                Availability.objects.get_or_create(
                    user=user,
                    day_of_week=day,
                    defaults={'start_time': time(9, 0), 'end_time': time(17, 0), 'is_available': True}
                )

            login(request, user)
            serializer = UserSerializer(user)
            return Response({
                'message': 'Account created and logged in successfully!',
                'user': serializer.data
            }, status=status.HTTP_201_CREATED)
        except Exception as exc:
            return Response({'error': f'Failed to create user: {str(exc)}'}, status=status.HTTP_400_BAD_REQUEST)

class FirebaseLoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        id_token = request.data.get('id_token')
        if not id_token:
            return Response({'error': 'id_token is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        user, decoded_token = verify_firebase_id_token(id_token)
        if not user:
            return Response({'error': 'Invalid Firebase Token'}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Log in via Django session
        login(request, user)
        serializer = UserSerializer(user)
        return Response({
            'message': 'Login successful',
            'user': serializer.data
        })

class DemoLoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username', 'rahul')
        email = request.data.get('email', f"{username.lower()}@company.com")
        first_name = request.data.get('first_name', username.capitalize())
        department = request.data.get('department', 'Engineering')
        job_role = request.data.get('job_role', 'Senior Manager')

        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'first_name': first_name,
                'employee_id': f"EMP-{User.objects.count()+1:04d}",
                'department': department,
                'job_role': job_role,
            }
        )
        login(request, user)
        serializer = UserSerializer(user)
        return Response({
            'message': f'Logged in as demo user {user.username}',
            'user': serializer.data
        })

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({'message': 'Logged out successfully'})

class CurrentUserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        user = request.user
        data = request.data
        
        fields = ['first_name', 'last_name', 'department', 'job_role', 'status', 'time_zone', 'work_start_time', 'work_end_time']
        for field in fields:
            if field in data:
                setattr(user, field, data[field])
        user.save()
        
        return Response(UserSerializer(user).data)

class UserListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        users = User.objects.all().order_by('first_name', 'username')
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

class AvailabilityUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        availabilities = Availability.objects.filter(user=request.user).order_by('day_of_week')
        serializer = AvailabilitySerializer(availabilities, many=True)
        return Response(serializer.data)

    def post(self, request):
        # Update or create weekly availability slots
        slots = request.data.get('slots', [])
        user = request.user
        
        for slot in slots:
            day_of_week = slot.get('day_of_week')
            start_time = slot.get('start_time', '09:00:00')
            end_time = slot.get('end_time', '17:00:00')
            is_available = slot.get('is_available', True)
            
            Availability.objects.update_or_create(
                user=user,
                day_of_week=day_of_week,
                defaults={
                    'start_time': start_time,
                    'end_time': end_time,
                    'is_available': is_available
                }
            )
            
        availabilities = Availability.objects.filter(user=user).order_by('day_of_week')
        return Response(AvailabilitySerializer(availabilities, many=True).data)

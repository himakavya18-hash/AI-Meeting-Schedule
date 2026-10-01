from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from accounts.services import verify_firebase_id_token

class FirebaseOrSessionAuthentication(BaseAuthentication):
    def authenticate(self, request):
        # 1. Check Bearer token in HTTP Authorization header
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            user, token_data = verify_firebase_id_token(token)
            if user:
                return (user, None)
            else:
                raise AuthenticationFailed('Invalid or expired Firebase ID Token')
        
        # 2. Check standard underlying Django HttpRequest session user
        django_request = getattr(request, '_request', request)
        if hasattr(django_request, 'user') and django_request.user and django_request.user.is_authenticated:
            return (django_request.user, None)
            
        return None

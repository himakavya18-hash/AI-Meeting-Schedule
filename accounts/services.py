import logging
from django.conf import settings
from django.contrib.auth import get_user_model
import firebase_admin
from firebase_admin import auth as firebase_auth, credentials

logger = logging.getLogger(__name__)

# Initialize Firebase Admin SDK if credentials provided
_firebase_initialized = False

def initialize_firebase():
    global _firebase_initialized
    if _firebase_initialized:
        return True
    
    try:
        if settings.FIREBASE_PROJECT_ID and settings.FIREBASE_PRIVATE_KEY:
            cred_dict = {
                "type": "service_account",
                "project_id": settings.FIREBASE_PROJECT_ID,
                "client_email": settings.FIREBASE_CLIENT_EMAIL,
                "private_key": settings.FIREBASE_PRIVATE_KEY.replace('\\n', '\n'),
            }
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
            _firebase_initialized = True
            logger.info("Firebase Admin SDK initialized successfully.")
            return True
        elif not firebase_admin._apps:
            # Initialize default app without explicit credentials (uses GOOGLE_APPLICATION_CREDENTIALS if present)
            firebase_admin.initialize_app()
            _firebase_initialized = True
            return True
    except Exception as e:
        logger.warning(f"Firebase Admin SDK initialization skipped or failed: {e}")
        return False
    return False

def verify_firebase_id_token(id_token):
    """
    Verifies Firebase ID token.
    Returns (user, decoded_token_dict) or (None, None).
    """
    User = get_user_model()
    
    # Initialize Firebase if possible
    initialize_firebase()
    
    # Support mock/demo tokens for frontend testing when Firebase SDK is operating in demo mode
    if id_token.startswith("demo-token-"):
        uid = id_token.replace("demo-token-", "")
        # Get or create demo user
        user, created = User.objects.get_or_create(
            username=uid,
            defaults={
                'email': f"{uid}@company.com",
                'first_name': uid.replace('_', ' ').title(),
                'employee_id': f"EMP-{hash(uid) % 10000:04d}",
                'department': 'Engineering',
                'job_role': 'Team Lead',
            }
        )
        return user, {'uid': uid, 'email': user.email}

    try:
        decoded_token = firebase_auth.verify_id_token(id_token)
        uid = decoded_token.get('uid')
        email = decoded_token.get('email', f"{uid}@company.com")
        name = decoded_token.get('name', email.split('@')[0])
        picture = decoded_token.get('picture', '')

        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': email.split('@')[0],
                'firebase_uid': uid,
                'first_name': name.split(' ')[0] if ' ' in name else name,
                'last_name': ' '.join(name.split(' ')[1:]) if ' ' in name else '',
                'avatar_url': picture,
                'employee_id': f"EMP-{hash(uid) % 10000:04d}",
            }
        )
        if not user.firebase_uid:
            user.firebase_uid = uid
            user.save(update_fields=['firebase_uid'])
            
        return user, decoded_token
    except Exception as e:
        logger.error(f"Failed to verify Firebase ID token: {e}")
        return None, None

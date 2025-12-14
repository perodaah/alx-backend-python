from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import SessionAuthentication

class CustomJWTAuthentication(JWTAuthentication):
    """
    Extend JWTAuthentication if you need custom logic.
    """
    pass

class CustomSessionAuthentication(SessionAuthentication):
    """
    Extend SessionAuthentication if you need custom logic.
    """
    pass

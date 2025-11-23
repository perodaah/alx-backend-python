# chats/middleware.py
from datetime import datetime
import time
from django.http import HttpResponseForbidden
import logging
from django.http import JsonResponse
from collections import defaultdict

# Configure the logger
logger = logging.getLogger(__name__)
handler = logging.FileHandler('requests.log')  # Log file in project root
formatter = logging.Formatter('%(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response  # Django passes the next middleware/view

    def __call__(self, request):
        # Determine user
        if request.user.is_authenticated:
            user = request.user.email  # or request.user.username
        else:
            user = "Anonymous"

        # Log the request
        logger.info(f"{datetime.now()} - User: {user} - Path: {request.path}")

        # Call the next middleware or view
        response = self.get_response(request)
        return response
class RestrictAccessByTimeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response  # store the next middleware / view

    def __call__(self, request):
        # Get current server time
        now = datetime.now().time()

        # Define allowed hours (6 AM to 9 PM)
        start_hour = 6   # 6 AM
        end_hour = 21    # 9 PM

        # Check if current hour is outside allowed range
        if now.hour < start_hour or now.hour >= end_hour:
            return HttpResponseForbidden(
                "Access to the messaging app is restricted at this hour."
            )

        # Otherwise, continue to the next middleware or view
        response = self.get_response(request)
        return response
class OffensiveLanguageMiddleware:
    """
    Limits number of POST requests (messages) per IP address.
    Allows 5 messages per minute per IP.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        # Store message timestamps per IP
        self.ip_message_times = defaultdict(list)

    def __call__(self, request):
        if request.method == "POST" and request.path.startswith("/api/messages/"):
            ip = self.get_client_ip(request)
            now = time.time()
            
            # Remove timestamps older than 60 seconds
            self.ip_message_times[ip] = [t for t in self.ip_message_times[ip] if now - t < 60]

            if len(self.ip_message_times[ip]) >= 5:
                return JsonResponse({"error": "Message limit exceeded. Try again later."}, status=429)
            
            # Record current message timestamp
            self.ip_message_times[ip].append(now)
        
        response = self.get_response(request)
        return response

    def get_client_ip(self, request):
        # X-Forwarded-For header if behind proxy, else remote_addr
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
class RolepermissionMiddleware:
    """
    Restricts actions based on user role.
    Only allows 'admin' or 'moderator'.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check user role if authenticated
        if request.user.is_authenticated:
            role = getattr(request.user, "role", None)
            restricted_paths = ["/api/conversations/", "/api/messages/"]  # example paths to protect
            
            for path in restricted_paths:
                if request.path.startswith(path) and role not in ["admin", "moderator"]:
                    return JsonResponse({"error": "Forbidden. Admin or moderator only."}, status=403)

        response = self.get_response(request)
        return response

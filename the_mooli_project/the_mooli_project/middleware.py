from django.utils import translation
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class UserLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # First handle language for unauthenticated users
        language = request.session.get(settings.LANGUAGE_SESSION_KEY)
        if language:
            translation.activate(language)
            request.LANGUAGE_CODE = language
        
        # Then check for authenticated users
        if hasattr(request, 'user') and request.user.is_authenticated:
            try:
                profile = request.user.userprofile
                user_language = profile.default_language
                translation.activate(user_language)
                request.LANGUAGE_CODE = user_language
                request.session[settings.LANGUAGE_SESSION_KEY] = user_language  # Keep session in sync
            except Exception:
                # If any error occurs with profile, fall back to session language
                pass
        
        response = self.get_response(request)
        return response

class LogRequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == "POST" and request.path == "/":
            logger.warning(f"Unexpected POST to / from {request.META.get('REMOTE_ADDR')} with headers: {dict(request.headers)}")
        return self.get_response(request)
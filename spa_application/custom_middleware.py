from django.conf import settings
from django.contrib.sessions.middleware import SessionMiddleware


class CustomSessionMiddleware(SessionMiddleware):
    def process_request(self, request):
        session_key = request.COOKIES.get(settings.SESSION_COOKIE_NAME)
        if session_key is None:
            request.session = self.SessionStore(session_key)
            request.session.create()
        else:
            request.session = self.SessionStore(session_key)

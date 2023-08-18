from django.contrib.auth import get_user_model
from rest_framework.authentication import BaseAuthentication

from accounts.models import CustomSession


class CustomSessionAuthentication(BaseAuthentication):
    def authenticate(self, request, *args, **kwargs) -> tuple | None:
        session_id = request.COOKIES.get('sessionid')
        if not session_id:
            return None
        user = self.get_user_by_session_id(session_id)
        if not user:
            return None
        return user, None

    @staticmethod
    def get_user_by_session_id(session_id: str):
        try:
            session = CustomSession.objects.only('user_id').get(session_key=session_id)
        except CustomSession.DoesNotExist:
            return None

        user_model = get_user_model()
        try:
            user = (
                user_model.objects
                .select_related('invite_code')
                .only('id', 'invited_by_id', 'phone_number', 'invite_code__invite_code')
                .get(id=session.user_id)
            )
        except user_model.DoesNotExist:
            return None
        return user

    def authenticate_header(self, request):
        return 'sessionid'

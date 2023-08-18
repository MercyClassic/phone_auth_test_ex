import uuid
from datetime import datetime, timedelta
from typing import Type

from django.contrib.sessions.models import Session

from .models import AuthModel, InviteCode, TemporarilyVerifyCode, CustomSession


class AuthRepository:
    """ USER ACTIONS """
    def get_user_by_phone_number(self, phone_number: str) -> Type[AuthModel] | None:
        try:
            user = AuthModel.objects.get(phone_number=phone_number)
        except AuthModel.DoesNotExist:
            return None
        return user

    def save_user_to_db(
            self,
            phone_number: str,
    ) -> int:
        user = AuthModel(phone_number=phone_number)
        user.save()
        return user.pk

    """ INVITE CODE ACTIONS """
    def save_invite_code_to_db(
            self,
            user_id: int,
            invite_code: str,
    ) -> None:
        InviteCode.objects.create(user_id=user_id, invite_code=invite_code)

    def get_invite_code(self, invite_code: str):
        try:
            invite_code = (
                InviteCode.objects
                .select_related('user')
                .only('id', 'user_id', 'user__invited_by')
                .get(invite_code=invite_code)
            )
        except InviteCode.DoesNotExist:
            return None
        return invite_code

    def get_inviter(self, inviter_id: int) -> Type[AuthModel]:
        return (
            AuthModel.objects
            .select_related('invite_code')
            .only('id', 'invite_code__invite_code')
            .get(id=inviter_id)
        )

    def get_invited_users(self, inviter_id: int):
        return (
            AuthModel.objects
            .only('phone_number')
            .filter(invited_by_id=inviter_id)
        )

    """ VERIFY CODE ACTIONS """
    def save_verify_code_to_db(
            self,
            user_id: int,
            verify_code: int,
    ) -> None:
        TemporarilyVerifyCode.objects.create(user_id=user_id, verify_code=verify_code)

    def get_verify_code(self, verify_code: int) -> Type[TemporarilyVerifyCode] | None:
        try:
            verify_code = TemporarilyVerifyCode.objects.get(verify_code=verify_code)
        except TemporarilyVerifyCode.DoesNotExist:
            return None
        return verify_code

    def delete_verify_code(self, verify_code: int, user_id: int) -> None:
        TemporarilyVerifyCode.objects.filter(verify_code=verify_code, user_id=user_id).delete()

    def get_session_by_user_id(self, user_id: int) -> Type[Session] | None:
        session = CustomSession.objects.filter(user_id=user_id)
        if len(session):
            return session[0]

    def create_session(self, user_id: int) -> Type[Session]:
        session = CustomSession.objects.create(
            user_id=user_id,
            session_key=str(uuid.uuid4()),
            expire_date=datetime.utcnow() + timedelta(days=365),
        )
        return session

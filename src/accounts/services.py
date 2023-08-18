import random
import re
import string
from typing import Type

from .exceptions import (
    NotAuthenticated,
    AlreadyInvited,
    CantInviteItSelf,
    CantBeInvitedByYoursInvitedUser,
    CodeNotFound,
)
from django.contrib.sessions.models import Session

from .models import AuthModel
from .repositories import AuthRepository


class AuthService:
    def __init__(self):
        self.repo = AuthRepository()

    @staticmethod
    def normalize_phone_number(phone_number: str) -> str:
        phone_number = re.sub(r'[() -]*', '', phone_number)

        if phone_number[0] != '+':
            phone_number = f'+{phone_number}'

        return f'+7{phone_number[2:]}'

    def create_user(self, phone_number: str) -> int:
        invite_code = self.generate_invite_code()
        normalized_phone_number = self.normalize_phone_number(phone_number)
        user_id = self.repo.save_user_to_db(phone_number=normalized_phone_number)
        self.repo.save_invite_code_to_db(invite_code=invite_code, user_id=user_id)
        return user_id

    def authorize(self, phone_number: str) -> int:
        normalized_phone_number = self.normalize_phone_number(phone_number)
        user = self.repo.get_user_by_phone_number(phone_number=normalized_phone_number)
        if not user:
            user_id = self.create_user(phone_number)
        else:
            user_id = user.pk

        verify_code = self.generate_verify_code()
        self.repo.save_verify_code_to_db(verify_code=verify_code, user_id=user_id)
        """ FAKE MESSAGE SENDING, MUST RETURN NONE """
        return verify_code

    def verify(self, verify_code: int) -> int:
        code_instance = self.repo.get_verify_code(verify_code=verify_code)
        if not code_instance:
            raise NotAuthenticated

        user_id = code_instance.user_id
        self.repo.delete_verify_code(verify_code=verify_code, user_id=user_id)
        return user_id

    def create_session_id_by_user_id(self, user_id: int) -> Type[Session]:
        session = self.repo.get_session_by_user_id(user_id)
        if not session:
            session = self.repo.create_session(user_id)
        return session

    def get_invitation_code(self, user: AuthModel) -> str | None:
        if not user.is_invited:
            return None
        inviter = self.repo.get_inviter(inviter_id=user.invited_by_id)
        return inviter.invite_code.invite_code

    def get_invited_users(self, inviter_id: int):
        return self.repo.get_invited_users(inviter_id=inviter_id)

    def set_invite_code(self, user: AuthModel, invite_code: str) -> None:
        if user.is_invited:
            raise AlreadyInvited
        db_instance = self.repo.get_invite_code(invite_code)
        if not db_instance:
            raise CodeNotFound

        if db_instance.user_id == user.pk:
            raise CantInviteItSelf

        if db_instance.user.invited_by_id == user.pk:
            raise CantBeInvitedByYoursInvitedUser

        user.invited_by_id = db_instance.user_id
        user.save()

    @staticmethod
    def generate_invite_code() -> str:
        return ''.join(random.choices(string.ascii_letters + string.digits, k=6))

    @staticmethod
    def generate_verify_code() -> int:
        return random.randint(1000, 10_000)

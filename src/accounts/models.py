from django.contrib.sessions.base_session import AbstractBaseSession
from django.utils import timezone
from django.core.validators import MinLengthValidator
from django.db import models

from .managers import AuthModelManager


class AuthModel(models.Model):
    phone_number = models.CharField(
        max_length=20,
        validators=[MinLengthValidator(11)],
        unique=True,
    )
    invited_by = models.OneToOneField(
        'self',
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
    )

    objects = AuthModelManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    def __str__(self):
        return f'{self.phone_number}'

    @property
    def is_invited(self):
        return self.invited_by_id is not None

    @property
    def is_anonymous(self):
        return self.phone_number is None

    @property
    def is_authenticated(self):
        return self.phone_number is not None


class InviteCode(models.Model):
    user = models.OneToOneField(
        'accounts.AuthModel',
        on_delete=models.PROTECT,
        related_name='invite_code',
    )
    invite_code = models.CharField(max_length=6, validators=[MinLengthValidator(6)])

    def __str__(self):
        return f'{self.user_id} - {self.invite_code}'


class TemporarilyVerifyCode(models.Model):
    user = models.ForeignKey(
        'accounts.AuthModel',
        on_delete=models.CASCADE,
        related_name='verify_codes',
    )
    created_at = models.DateTimeField(default=timezone.now())
    verify_code = models.IntegerField()

    def __str__(self):
        return f'{self.user_id} - {self.verify_code}'


class CustomSession(AbstractBaseSession):
    user = models.OneToOneField('accounts.AuthModel', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user_id}'

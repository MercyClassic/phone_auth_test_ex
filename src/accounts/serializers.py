from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from accounts.models import (
    AuthModel,
    TemporarilyVerifyCode,
    InviteCode,
)
from accounts.validators import phone_validator


class AuthorizationSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20, min_length=11)

    def validate_phone_number(self, value):
        value = phone_validator(value)
        if not value:
            raise ValidationError
        return value[0]


class InvitedUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthModel
        fields = ('phone_number', )


class VerifyCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemporarilyVerifyCode
        fields = ('verify_code', )


class InviteCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = InviteCode
        fields = ('invite_code', )


class ProfileSerializer(serializers.ModelSerializer):
    invitation_code = serializers.SerializerMethodField()
    invite_code = serializers.SerializerMethodField()
    invited_users = serializers.SerializerMethodField()

    class Meta:
        model = AuthModel
        fields = ('phone_number', 'invite_code', 'invitation_code', 'invited_users')

    def get_invitation_code(self, *args, **kwargs):
        return self.context.get('invitation_code')

    def get_invite_code(self, instance):
        return instance.invite_code.invite_code

    def get_invited_users(self, *args, **kwargs):
        return self.context.get('invited_users')

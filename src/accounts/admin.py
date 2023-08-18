from django.contrib import admin

from .models import AuthModel, InviteCode, TemporarilyVerifyCode

admin.site.register(AuthModel)
admin.site.register(InviteCode)
admin.site.register(TemporarilyVerifyCode)

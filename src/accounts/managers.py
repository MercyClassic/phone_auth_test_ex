from django.contrib.auth.models import UserManager


class AuthModelManager(UserManager):
    def _create_user(self, phone_number, **extra_fields):
        user = self.model(phone_number=phone_number, **extra_fields)
        user.save(using=self._db)
        return user

    def create_user(self, phone_number=None, **extra_fields):
        return self._create_user(phone_number, **extra_fields)

    def create_superuser(self, phone_number=None, **extra_fields):
        return self._create_user(phone_number, **extra_fields)

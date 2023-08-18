from datetime import datetime, timedelta

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from accounts.models import TemporarilyVerifyCode, InviteCode, AuthModel, CustomSession


class AuthTests(APITestCase):
    def parametrize_authorization(self, phone_number: str):
        response = self.client.post(
            path=reverse('api-authorization'),
            data={'phone_number': phone_number},
        )
        return response

    def test_authorization(self):
        """ PHONE NUMBER TOO LONG """
        response = self.parametrize_authorization('+7-123-123-13-13-13')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        """ PHONE NUMBER IS OK """
        response = self.parametrize_authorization('+7 (123) 123-13-13')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def parametrize_verify(self, verify_code: int):
        response = self.client.post(
            path=reverse('api-verify'),
            data={'verify_code': verify_code},
        )
        return response

    def test_verify(self):
        """ INVALID VERIFY CODE """
        response = self.parametrize_verify(1234)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        """ VALID VERIFY CODE """

        user = AuthModel.objects.create(phone_number='+71231231313')
        TemporarilyVerifyCode.objects.create(user_id=user.pk, verify_code=1111)

        response = self.parametrize_verify(1111)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('sessionid', response.cookies)

    def parametrize_set_invite_code(self, invite_code: str):
        response = self.client.post(
            path=reverse('api-me'),
            data={'invite_code': invite_code},
        )
        return response

    def test_profile(self):
        inviter = AuthModel.objects.create(phone_number='+71111111111')
        InviteCode.objects.create(user_id=inviter.pk, invite_code='111aaa')
        inviter_session = CustomSession.objects.create(
            user_id=inviter.pk,
            session_key='1',
            expire_date=datetime.utcnow() + timedelta(seconds=5),
        )

        invited = AuthModel.objects.create(phone_number='+72222222222')
        InviteCode.objects.create(user_id=invited.pk, invite_code='222bbb')
        invited_session = CustomSession.objects.create(
            user_id=invited.pk,
            session_key='2',
            expire_date=datetime.utcnow() + timedelta(seconds=5),
        )

        """ INVALID INVITE CODE """
        self.client.cookies['sessionid'] = inviter_session.session_key
        response = self.parametrize_set_invite_code('sd421s')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data.get('detail'), 'Code not found')

        """ TRY TO INVITE ITSELF """
        self.client.cookies['sessionid'] = inviter_session.session_key
        response = self.parametrize_set_invite_code('111aaa')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data.get('detail'), "You can't invite yourself")

        """ IS OK """
        self.client.cookies['sessionid'] = invited_session.session_key
        response = self.parametrize_set_invite_code('111aaa')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        """ GET PROFILE INVITED PROFILE """
        self.client.cookies['sessionid'] = invited_session.session_key
        response = self.client.get(reverse('api-me'))
        self.assertEqual(
            response.data,
            {
                'phone_number': '+72222222222',
                'invite_code': '222bbb',
                'invitation_code': '111aaa',
                'invited_users': [],
            },
        )

        """ GET PROFILE INVITER PROFILE """
        self.client.cookies['sessionid'] = inviter_session.session_key
        response = self.client.get(reverse('api-me'))
        self.assertEqual(
            response.data,
            {
                'phone_number': '+71111111111',
                'invite_code': '111aaa',
                'invitation_code': None,
                'invited_users': [
                    {'phone_number': '+72222222222'},
                ],
            },
        )

        """ TRY TO SET INVITE CODE WHEN USER ALREADY HAVE BEEN INVITED  """
        self.client.cookies['sessionid'] = invited_session.session_key
        response = self.parametrize_set_invite_code('111aaa')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data.get('detail'), 'You have been already invited')

        """ INVITER TRY TO SET INVITED USER'S CODE  """
        self.client.cookies['sessionid'] = inviter_session.session_key
        response = self.parametrize_set_invite_code('222bbb')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data.get('detail'),
            "You can't be invited by user who was invited by you",
        )

import time

from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .serializers import (
    AuthorizationSerializer,
    ProfileSerializer,
    VerifyCodeSerializer,
    InviteCodeSerializer,
    InvitedUserSerializer,
)
from .services import AuthService
from utils.CustomThread import CustomThread


class AuthorizationAPIView(GenericAPIView):
    serializer_class = AuthorizationSerializer
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            def worker():
                time.sleep(2)
                service = AuthService()
                """ FAKE MESSAGE SENDING, IN PRODUCTION THIS CODE SHOULDN'T BR SHOWN """
                verify_code = service.authorize(**serializer.validated_data)
                return Response(status=status.HTTP_200_OK, data={'verify_code': verify_code})

            thread = CustomThread(target=worker)
            thread.start()
            return thread.join()

        return Response(status=status.HTTP_400_BAD_REQUEST)


class VerifyAPIView(GenericAPIView):
    serializer_class = VerifyCodeSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            code = serializer.validated_data.get('verify_code')
            service = AuthService()

            user_id = service.verify(verify_code=code)
            if user_id:
                session_id = service.create_session_id_by_user_id(user_id=user_id)

                response = Response(status=status.HTTP_200_OK)
                response.set_cookie('sessionid', session_id, httponly=True)
                return response
        return Response(status=status.HTTP_403_FORBIDDEN)


class ProfileAPIView(GenericAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ProfileSerializer
        elif self.request.method == 'POST':
            return InviteCodeSerializer

    def get(self, request, *args, **kwargs):
        service = AuthService()

        invitation_code = service.get_invitation_code(request.user)
        invited_users = InvitedUserSerializer(
            service.get_invited_users(request.user.pk),
            many=True,
        )

        serializer = self.get_serializer(request.user)

        serializer.context['invitation_code'] = invitation_code
        serializer.context['invited_users'] = invited_users.data

        return Response(status=status.HTTP_200_OK, data=serializer.data)

    def post(self, request, *args, **kwargs):
        service = AuthService()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            service.set_invite_code(
                user=request.user,
                invite_code=serializer.validated_data.get('invite_code'),
            )
            return Response(status=status.HTTP_200_OK)

        return Response(status=status.HTTP_400_BAD_REQUEST)

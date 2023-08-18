from django.urls import path
from . import views

urlpatterns = [
    path('api/v1/authorization', views.AuthorizationAPIView.as_view(), name='api-authorization'),
    path('api/v1/verify', views.VerifyAPIView.as_view(), name='api-verify'),
    path('api/v1/me', views.ProfileAPIView.as_view(), name='api-me'),
]

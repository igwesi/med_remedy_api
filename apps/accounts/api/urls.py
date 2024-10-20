from django.urls import path

from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)

from .views import (
    LoginView,
    RegisterView,
    UserLogoutView,
    UserProfileView,
    UserChangePasswordView,
    SendPasswordResetEmailView,
    UserPasswordResetView
)

app_name = 'accounts'

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('me/', UserProfileView.as_view(), name='profile'),
    path('register/', RegisterView.as_view(), name='register'),

    path('password/reset/', SendPasswordResetEmailView.as_view(), name='send-reset-password-email'),
    path('reset-password/<str:uid>/<str:token>/', UserPasswordResetView.as_view(), name='reset-password'),
    path('change-password/', UserChangePasswordView.as_view(), name='changepassword'),

    path('refresh/', TokenRefreshView.as_view(), name='refresh'),
    path('verify/', TokenVerifyView.as_view(), name='verify'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
]
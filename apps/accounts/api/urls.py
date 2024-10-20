from django.urls import path

from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
    token_blacklist,
)

from .views import (
    LoginView,
    RegisterView,
    UserProfileView,
    UserChangePasswordView,
    SendPasswordResetEmailView,
    UserPasswordResetView
)

app_name = 'accounts'

urlpatterns = [
    path('me/', UserProfileView.as_view(), name='profile'),
    path('login/', LoginView.as_view(), name='login'),
    
    path('change-password/', UserChangePasswordView.as_view(), name='changepassword'),
    path('reset-password/', SendPasswordResetEmailView.as_view(), name='send-reset-password-email'),
    path('reset-password/confirm/', UserPasswordResetView.as_view(), name='reset-password'),

    path('register/', RegisterView.as_view(), name='register'),
    path('refresh/', TokenRefreshView.as_view(), name='refresh'),
    path('verify/', TokenVerifyView.as_view(), name='verify'),
]
from django.urls import path
from .views import *
urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('resend-otp/', ResendOTPView.as_view(), name='resend-otp'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('me/', UserProfileView.as_view(), name='user-profile'),
    path('update-profile-picture/', UpdateProfilePictureView.as_view(), name='update-profile-picture'),
    path('google-auth/', GoogleAuthView.as_view(), name='google-auth'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    path('has-password/', HasPasswordView.as_view(), name='has-password'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),

]

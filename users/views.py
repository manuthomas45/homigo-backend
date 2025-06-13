import cloudinary
import cloudinary.uploader
from .serializers import *
from .models import OTP
from django.core.mail import send_mail
from django.conf import settings
import random
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import *
from datetime import timedelta
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from google.oauth2 import id_token
from google.auth.transport.requests import Request as GoogleRequest
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
import re
import logging



User = get_user_model()
logger=logging.getLogger('homigo')
class RegisterView(APIView):
    permission_classes = [AllowAny]  # Allow unauthenticated users to register

    def post(self, request):
        logger.info("Received registration request.")
        logger.debug(f"Request data: {request.data}")
        serializer = UserRegisterSerializer(data=request.data)
        print("Serializer:", serializer)
        if serializer.is_valid():
            user = serializer.save()

            # Generate and store OTP
            otp = str(random.randint(100000, 999999))
            OTP.objects.create(email=user.email, otp=otp)
            print("Generated OTP:", otp)

            # Send OTP email
            try:
                send_mail(
                    'Your HomiGo OTP',
                    f'Your OTP for registration is: {otp}',
                    settings.EMAIL_HOST_USER,
                    [user.email],
                    fail_silently=False,
                )
                print("Email sent successfully to:", user.email)
            except Exception as e:
                print("Failed to send email:", str(e))
                return Response(
                    {'message': 'User registered, but failed to send OTP email. Please try again.'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            return Response({'message': 'User registered. OTP sent to email.'}, status=status.HTTP_201_CREATED)
        logger.warning(f"Registration failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyOTPView(APIView):
    permission_classes = [AllowAny]  # Allow unauthenticated users to verify OTP

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp = serializer.validated_data['otp']

            # Check if OTP exists and matches
            otp_record = OTP.objects.filter(email=email, otp=otp).first()
            if not otp_record:
                return Response({'message': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)

            # Check if OTP has expired (2 minutes = 120 seconds)
            time_limit = timedelta(minutes=2)
            if timezone.now() - otp_record.created_at > time_limit:
                return Response({'message': 'OTP has expired'}, status=status.HTTP_400_BAD_REQUEST)

            # Mark user as verified
            user = User.objects.get(email=email)
            user.isVerified = True
            user.status = 'active'
            user.save()

            # Delete the OTP after verification
            otp_record.delete()

            return Response({'message': 'OTP verified successfully'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ResendOTPView(APIView):
    permission_classes = [AllowAny]  # Allow unauthenticated users to resend OTP

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'message': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if user exists
        user = User.objects.filter(email=email).first()
        if not user:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        # Delete any existing OTP for this email
        OTP.objects.filter(email=email).delete()

        # Generate and store new OTP
        otp = str(random.randint(100000, 999999))
        OTP.objects.create(email=email, otp=otp)
        print("Generated new OTP:", otp)

        # Send new OTP email
        try:
            send_mail(
                'Your HomiGo OTP',
                f'Your new OTP for registration is: {otp}',
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
            )
            print("New OTP email sent successfully to:", email)
        except Exception as e:
            print("Failed to send new ОTP email:", str(e))
            return Response(
                {'message': 'Failed to send new OTP email. Please try again.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response({'message': 'New OTP sent to email.'}, status=status.HTTP_200_OK)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({'message': 'Email and password are required'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if email exists
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'message': 'Email is incorrect'}, status=status.HTTP_401_UNAUTHORIZED)

        # Authenticate user (check password)
        user = authenticate(request, email=email, password=password)
        if not user:
            return Response({'message': 'Password is incorrect'}, status=status.HTTP_401_UNAUTHORIZED)

        # if not user.isVerified:
        #     return Response({'message': 'Please verify your email before logging in'}, status=status.HTTP_403_FORBIDDEN)

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        # Prepare response
        response = Response({
            'message': 'Login successful',
            'access_token': access_token,
            'user': {
                'email': user.email,
                'role': user.role,
            }
        }, status=status.HTTP_200_OK)

        # Set refresh_token in HTTP-only cookie
        response.set_cookie(
            key='refresh_token',
            value=refresh_token,
            httponly=True,
            secure=False,
            samesite='Lax',
            max_age=24 * 60 * 60
        )

        return response


class RefreshTokenView(APIView):
    permission_classes = [AllowAny]  # Allow unauthenticated users to refresh token (uses cookie)

    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return Response({'message': 'Refresh token not found'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)
            new_refresh_token = str(refresh)

            # Prepare response with access token in body
            response = Response({
                'message': 'Token refreshed',
                'access_token': access_token,
            }, status=status.HTTP_200_OK)

            # Set new refresh_token in cookie
            response.set_cookie(
                key='refresh_token',
                value=new_refresh_token,
                httponly=True,
                secure=False,
                samesite='Lax',
                max_age=24 * 60 * 60
            )

            return response
        except Exception as e:
            return Response({'message': 'Invalid refresh token'}, status=status.HTTP_401_UNAUTHORIZED)

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]  # Only authenticated users can view/update profile

    def get(self, request):
        user = request.user
        profile_picture_url = None
        if user.profilePicture:
            # Apply transformation: resize to 150x150, crop to fit
            profile_picture_url = user.profilePicture.build_url(width=150, height=150, crop='fit')
        
        return Response({
            'email': user.email,
            'firstName': user.firstName,
            'lastName': user.lastName,
            'phoneNumber': user.phoneNumber,
            'role': user.role,
            'profilePicture': profile_picture_url,
        }, status=status.HTTP_200_OK)

    def put(self, request):
        user = request.user
        serializer = UserProfileSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            # Prevent email updates
            if 'email' in request.data:
                return Response({'message': 'Email cannot be updated'}, status=status.HTTP_400_BAD_REQUEST)
            
            serializer.save()
            return Response({
                'message': 'Profile updated successfully',
                'user': serializer.data,
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UpdateProfilePictureView(APIView):
    permission_classes = [IsAuthenticated]  # Only authenticated users can update profile picture

    def post(self, request):
        user = request.user
        if 'profilePicture' not in request.FILES:
            return Response({'message': 'No image file provided'}, status=status.HTTP_400_BAD_REQUEST)

        image = request.FILES['profilePicture']
        # Validate file type
        if not image.content_type.startswith('image/'):
            return Response({'message': 'File must be an image'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate file size (e.g., max 5MB)
        if image.size > 5 * 1024 * 1024:
            return Response({'message': 'Image size must be less than 5MB'}, status=status.HTTP_400_BAD_REQUEST)

        # Delete the old image from Cloudinary if it exists
        if user.profilePicture:
            try:
                public_id = user.profilePicture.public_id
                cloudinary.uploader.destroy(public_id)
            except Exception as e:
                print(f"Failed to delete old image: {e}")

        user.profilePicture = image
        user.save()
        profile_picture_url = user.profilePicture.build_url(width=150, height=150, crop='fit') if user.profilePicture else None
        return Response({
            'message': 'Profile picture updated successfully',
            'profilePicture': profile_picture_url,
        }, status=status.HTTP_200_OK)

class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')
        response = Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
        response.delete_cookie('refresh_token')

        if not refresh_token:
            return response

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception as e:
            print(f"Failed to blacklist token: {e}")

        return response



class GoogleAuthView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        credential = request.data.get('credential')
        client_id = request.data.get('client_id')

        if not credential or not client_id:
            return Response(
                {'message': 'Credential or client_id missing'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            idinfo = id_token.verify_oauth2_token(
                credential,
                GoogleRequest(),
                client_id
            )

            email = idinfo.get('email')
            first_name = idinfo.get('given_name', '')
            last_name = idinfo.get('family_name', '')

            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'firstName': first_name,  # Use firstName as per your model
                    'lastName': last_name,    # Use lastName as per your model
                    'role': 'user',
                    'phoneNumber': '',        # Required field; set to empty string
                    'status':'active',
                    'isVerified':True,
                }
            )

            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            response_data = {
                'access_token': access_token,
                'user': {
                    'email': user.email,
                    'role': user.role,
                }
            }

            response = Response(response_data, status=status.HTTP_200_OK)
            response.set_cookie(
                key='refresh_token',
                value=str(refresh),
                httponly=True,
                secure=False,
                samesite='Lax',
                max_age=24 * 60 * 60
            )

            return response

        except ValueError as e:
            return Response(
                {'message': 'Invalid Google token', 'details': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        


class ForgotPasswordView(APIView):
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
                token = PasswordResetToken.objects.create(user=user)
                reset_url = f"http://localhost:5173/reset-password?token={token.token}"
                send_mail(
                    subject="HomiGo Password Reset",
                    message=f"Click the link to reset your password: {reset_url}\nThis link will expire in 30 minutes.",
                    from_email="HomiGo <your-email@gmail.com>",
                    recipient_list=[email],
                    fail_silently=False,
                )
            except User.DoesNotExist:
                pass
            return Response({"message": "If an account exists, a reset link has been sent to your email."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ResetPasswordView(APIView):
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            token_value = serializer.validated_data['token']
            new_password = serializer.validated_data['new_password']
            token = PasswordResetToken.objects.get(token=token_value)
            user = token.user
            # Update password using set_password (hashes automatically)
            user.set_password(new_password)
            user.save()
            token.delete()
            print(f"Password updated for {user.email}: {user.password}")  # Debug log
            return Response({"message": "Password reset successful"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class HasPasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        has_password = user.has_usable_password()
        return Response({'hasPassword': has_password}, status=status.HTTP_200_OK)

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        data = request.data

        current_password = data.get('currentPassword')
        new_password = data.get('newPassword')
        confirm_password = data.get('confirmPassword')

        # If user has a password, verify the current password
        if user.has_usable_password():
            if not current_password:
                return Response(
                    {'error': 'Current password is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if not check_password(current_password, user.password):
                return Response(
                    {'error': 'Current password is incorrect'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Validate new password
        password_regex = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*])[A-Za-z\d!@#$%^&*]{8,}$'
        if not new_password or not confirm_password:
            return Response(
                {'error': 'New password and confirm password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not re.match(password_regex, new_password):
            return Response(
                {'error': 'Password must be at least 8 characters long and include uppercase, lowercase, digit, and special character'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if new_password != confirm_password:
            return Response(
                {'error': 'New password and confirm password do not match'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update password
        user.set_password(new_password)
        user.save()

        return Response({'message': 'Password updated successfully'}, status=status.HTTP_200_OK)
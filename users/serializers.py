from rest_framework import serializers
from .models import User, OTP

class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['firstName', 'lastName', 'email', 'password', 'phoneNumber']  # Removed profilePicture
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            firstName=validated_data['firstName'],
            lastName=validated_data['lastName'],
            phoneNumber=validated_data['phoneNumber'],
        )
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['firstName', 'lastName', 'phoneNumber']  # Only fields that can be updated

class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
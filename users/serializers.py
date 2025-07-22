from rest_framework import serializers
from .models import User, PasswordResetToken,Address
import cloudinary
import re
from technicians.models import ServiceCategory
from services.models import  ServiceType

class UserSerializer(serializers.ModelSerializer):
    profilePicture = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'firstName', 'lastName', 'email', 'phoneNumber', 'role', 'profilePicture']

    def get_profilePicture(self, obj):
        if obj.profilePicture:
            return cloudinary.CloudinaryImage(str(obj.profilePicture)).build_url()
        return None

class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['firstName', 'lastName', 'email', 'password', 'phoneNumber']
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
        fields = ['firstName', 'lastName', 'phoneNumber']

class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            return value  # Generic response for security
        return value

class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.UUIDField(required=True)
    new_password = serializers.CharField(min_length=8, required=True)

    def validate_new_password(self, value):
        if not any(char.isupper() for char in value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter")
        if not any(char.islower() for char in value):
            raise serializers.ValidationError("Password must contain at least one lowercase letter")
        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError("Password must contain at least one number")
        return value

    def validate_token(self, value):
        try:
            token = PasswordResetToken.objects.get(token=value)
            if token.is_expired():
                raise serializers.ValidationError("Token has expired")
        except PasswordResetToken.DoesNotExist:
            raise serializers.ValidationError("Invalid token")
        return value
    
class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'firstName', 'lastName', 'email', 'phoneNumber', 'role', 'profilePicture']
        read_only_fields = ['id', 'email', 'role']

    def validate_firstName(self, value):
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError("First name must be at least 2 characters long")
        if not re.match(r'^[A-Za-z]+$', value):
            raise serializers.ValidationError("First name must contain only letters")
        return value

    def validate_lastName(self, value):
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError("Last name must be at least 2 characters long")
        if not re.match(r'^[A-Za-z]+$', value):
            raise serializers.ValidationError("Last name must contain only letters")
        return value

    def validate_phoneNumber(self, value):
        if not value or not re.match(r'^\d{10}$', value):
            raise serializers.ValidationError("Phone number must be exactly 10 digits")
        return value


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'address', 'city', 'state', 'pincode', 'phone_number', 'is_default',]
        extra_kwargs = {
            'user': {'read_only': True},
            'is_default': {'read_only': True}  # Make is_default read-only in create/update
        }

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        # Do not set is_default here; let it default to False or handle via SetDefaultAddressView
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Exclude is_default from update to prevent accidental changes
        validated_data.pop('is_default', None)
        return super().update(instance, validated_data)
    


class ServiceTypeSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ServiceType
        fields = ['id', 'name', 'rate', 'description', 'image_url']

    def get_image_url(self, obj):
        return obj.image.url if obj.image else None

class UserServiceCategorySerializer(serializers.ModelSerializer):
    service_types = ServiceTypeSerializer(many=True, read_only=True)
    service_image_url = serializers.SerializerMethodField()

    class Meta:
        model = ServiceCategory
        fields = ['id', 'name', 'service_image_url', 'service_types']

    def get_service_image_url(self, obj):
        return obj.service_image.url if obj.service_image else None
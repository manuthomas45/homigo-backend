from rest_framework import serializers
from .models import ServiceCategory, TechnicianDetails
from users.models import User
from .models import TechnicianDetails
from users.serializers import UserSerializer
import cloudinary

class ServiceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCategory
        fields = ['id', 'name', 'service_image']

class TechnicianDetailsSerializerc(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=ServiceCategory.objects.all())
    aadhaar_card_picture = serializers.ImageField()
    certificate_picture = serializers.ImageField()

    class Meta:
        model = TechnicianDetails
        fields = [
            'category',
            'aadhaar_number',
            'aadhaar_card_picture',
            'certificate_picture',
            'city',
        ]

    def validate_aadhaar_number(self, value):
        if not value.isdigit() or len(value) != 12:
            raise serializers.ValidationError("Aadhaar number must be a 12-digit number")
        if TechnicianDetails.objects.filter(aadhaar_number=value).exists():
            raise serializers.ValidationError("Aadhaar number already exists")
        return value

    def validate_category(self, value):
        if not ServiceCategory.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Invalid category ID")
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        user.role = 'technician'
        user.save()
        technician_details = TechnicianDetails.objects.create(user=user, **validated_data)
        return technician_details



class TechnicianDetailsSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    category = serializers.CharField(source='category.name')
    aadhaar_card_picture = serializers.SerializerMethodField()
    certificate_picture = serializers.SerializerMethodField()

    class Meta:
        model = TechnicianDetails
        fields = ['user', 'category', 'aadhaar_number', 'aadhaar_card_picture', 'certificate_picture', 'wallet', 'city', 'is_verified', 'status']

    def get_aadhaar_card_picture(self, obj):
        if obj.aadhaar_card_picture:
            return cloudinary.CloudinaryImage(str(obj.aadhaar_card_picture)).build_url()
        return None

    def get_certificate_picture(self, obj):
        if obj.certificate_picture:
            return cloudinary.CloudinaryImage(str(obj.certificate_picture)).build_url()
        return None
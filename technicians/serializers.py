from rest_framework import serializers
from .models import Technician, TechnicianDetails
from django.contrib.auth.hashers import make_password

class TechnicianDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TechnicianDetails
        fields = ['aadhaar_number', 'aadhaar_card_picture', 'certificate_picture', 'city', 'longitude', 'latitude']

class TechnicianSerializer(serializers.ModelSerializer):
    details = TechnicianDetailsSerializer()

    class Meta:
        model = Technician
        fields = ['id', 'first_name', 'last_name', 'email', 'password', 'phone_number', 'category', 'details']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        details_data = validated_data.pop('details')
        validated_data['password'] = make_password(validated_data['password'])  # Hash password
        technician = Technician.objects.create(**validated_data)
        TechnicianDetails.objects.create(technician=technician, **details_data)
        return technician

class TechnicianLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

class TechnicianResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Technician
        fields = ['id', 'first_name', 'last_name', 'email', 'phone_number', 'category']
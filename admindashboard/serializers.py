from rest_framework import serializers
from users.models import User
from booking.models import Booking


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'firstName', 'lastName', 'email', 'phoneNumber', 'status']


class BookingSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    technician_name = serializers.SerializerMethodField()
    service_type_name = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Booking
        fields = ['id', 'user_name', 'technician_name', 'service_type_name', 
                 'category_name', 'amount', 'booking_date', 'status']
    
    def get_user_name(self, obj):
        return f"{obj.user.firstName} {obj.user.lastName}"
    
    def get_technician_name(self, obj):
        if obj.technician:
            return f"{obj.technician.user.firstName} {obj.technician.user.lastName}"
        return None
    
    def get_service_type_name(self, obj):
        return obj.service_type.name
    
    def get_category_name(self, obj):
        return obj.category.name
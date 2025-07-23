from rest_framework import serializers
from .models import Booking

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['id', 'category', 'service_type', 'user', 'address', 'status', 'amount', 'technician', 'booking_date']

    def create(self, validated_data):
        booking = Booking.objects.create(**validated_data)
        return booking
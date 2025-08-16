from rest_framework import serializers
from .models import Booking,Complaint

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['id', 'category', 'service_type', 'user', 'address', 'status', 'amount', 'technician', 'booking_date']

    def create(self, validated_data):
        booking = Booking.objects.create(**validated_data)
        return booking


class ComplaintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complaint
        fields = ['booking', 'user', 'technician', 'category', 'service_type', 'title', 'description']
        extra_kwargs = {
            'user': {'read_only': True},
            'technician': {'read_only': True},
            'category': {'read_only': True},
            'service_type': {'read_only': True}
        }
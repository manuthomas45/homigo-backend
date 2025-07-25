from django.db import models
from technicians.models import ServiceCategory
from services.models import ServiceType
from users.models import Address
from django.contrib.auth.models import User
from django.conf import settings
from technicians.models import TechnicianDetails


class Booking(models.Model):
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE)
    service_type = models.ForeignKey(ServiceType, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    address = models.ForeignKey(Address, on_delete=models.CASCADE)  
    status = models.CharField(
    max_length=20,
    choices=[
        ('pending', 'Pending'),
        ('cancelled', 'Cancelled'),
        ('booked', 'Booked'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed')
    ],
    default='pending' )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    technician = models.ForeignKey('technicians.TechnicianDetails', on_delete=models.SET_NULL, null=True, blank=True)
    booking_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Booking {self.id} - {self.service_type.name} for {self.user.email}"
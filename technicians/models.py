from django.db import models
from cloudinary.models import CloudinaryField

class Technician(models.Model):
    CATEGORY_CHOICES = [
        ('plumber', 'Plumber'),
        ('electrician', 'Electrician'),
        ('carpenter', 'Carpenter'),
        ('painter', 'Painter'),
    ]

    id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)  # Store hashed password
    phone_number = models.CharField(max_length=15)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    profile_picture = CloudinaryField('image', blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"


class TechnicianDetails(models.Model):
    id = models.AutoField(primary_key=True)
    technician = models.OneToOneField(Technician, on_delete=models.CASCADE, related_name='details')
    aadhaar_number = models.CharField(max_length=12, unique=True)
    aadhaar_card_picture = CloudinaryField('image')
    certificate_picture = CloudinaryField('image')
    wallet = models.FloatField(default=0.0)
    is_verified = models.BooleanField(default=False)
    status = models.CharField(max_length=20, default='offline')  
    city = models.CharField(max_length=100)
    longitude = models.FloatField()
    latitude = models.FloatField()

    def __str__(self):
        return f"Details for {self.technician.email}"
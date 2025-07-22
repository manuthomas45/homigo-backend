from django.db import models
from cloudinary.models import CloudinaryField
from users.models import User

class ServiceCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    service_image = CloudinaryField('image', blank=True, null=True)


    def __str__(self):
        return self.name

class TechnicianDetails(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='technician_details')
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, related_name='technicians')
    aadhaar_number = models.CharField(max_length=12, unique=True)
    aadhaar_card_picture = CloudinaryField('image')
    certificate_picture = CloudinaryField('image')
    wallet = models.FloatField(default=0.0)
    is_verified = models.BooleanField(default=False)
    status = models.CharField(max_length=20, default='offline')
    city = models.CharField(max_length=100)

    def __str__(self):
        return f"Details for {self.user.email}"
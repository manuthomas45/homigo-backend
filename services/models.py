from django.db import models
from technicians.models import ServiceCategory
import cloudinary.models

class ServiceType(models.Model):
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, related_name='service_types')
    name = models.CharField(max_length=100)
    rate = models.FloatField()  # Consider using DecimalField for precise financial calculations
    description = models.TextField(blank=True, null=True)  # Flexible text field for description
    image = cloudinary.models.CloudinaryField('image', blank=True, null=True)  # Cloudinary image field

    def __str__(self):
        return f"{self.name} ({self.category.name})"

    class Meta:
        unique_together = ('category', 'name')  # Enforces unique combination of category and name

    # Optional: Add a method to get the image URL if needed
    def get_image_url(self):
        if self.image:
            return self.image.url
        return None
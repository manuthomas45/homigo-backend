from rest_framework import serializers
from technicians.models import ServiceCategory
import cloudinary

class ServiceCategorySerializer(serializers.ModelSerializer):
    # Use a CharField for writing (to accept the public ID)
    service_image = serializers.CharField(allow_blank=True, required=False)

    class Meta:
        model = ServiceCategory
        fields = ['id', 'name', 'service_image']

    # Override to_representation to return the full Cloudinary URL
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if ret['service_image']:
            ret['service_image'] = cloudinary.CloudinaryImage(str(ret['service_image'])).build_url()
        return ret
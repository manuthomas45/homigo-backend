from rest_framework import serializers
from technicians.models import ServiceCategory
from services.models import ServiceType
import cloudinary

class ServiceCategorySerializer(serializers.ModelSerializer):
    service_image = serializers.ImageField(allow_null=True, required=False)

    class Meta:
        model = ServiceCategory
        fields = ['id', 'name', 'service_image']

    def create(self, validated_data):
        return ServiceCategory.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        if 'service_image' in validated_data:
            instance.service_image = validated_data['service_image']
        instance.save()
        return instance

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if ret['service_image']:
            ret['service_image'] = cloudinary.CloudinaryImage(str(ret['service_image'])).build_url()
        return ret

class ServiceTypeSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(allow_null=True, required=False)  # Field for image upload
    category = serializers.PrimaryKeyRelatedField(queryset=ServiceCategory.objects.all())

    class Meta:
        model = ServiceType
        fields = ['id', 'category', 'name', 'rate', 'description', 'image']

    def validate(self, data):
        # Check for unique combination of category and name
        exclude_instance = None
        if hasattr(self, 'instance') and self.instance is not None:
            exclude_instance = self.instance.id
        if ServiceType.objects.filter(category=data['category'], name=data['name']).exclude(id=exclude_instance).exists():
            raise serializers.ValidationError({
                "non_field_errors": ["The combination of category and name must be unique."]
            })
        return data

    def create(self, validated_data):
        # Extract image if present
        image = validated_data.pop('image', None)
        try:
            instance = ServiceType.objects.create(**validated_data)
            if image:
                instance.image = image
                instance.save(update_fields=['image'])  # Save only the image field
            return instance
        except Exception as e:
            raise serializers.ValidationError({"error": f"Failed to create service type: {str(e)}"})

    def update(self, instance, validated_data):
        instance.category = validated_data.get('category', instance.category)
        instance.name = validated_data.get('name', instance.name)
        instance.rate = validated_data.get('rate', instance.rate)
        instance.description = validated_data.get('description', instance.description)
        if 'image' in validated_data:
            instance.image = validated_data['image']
        instance.save()
        return instance

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if ret['image']:
            ret['image'] = cloudinary.CloudinaryImage(str(instance.image)).build_url()
        return ret
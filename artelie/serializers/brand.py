from rest_framework import serializers
from rest_framework.serializers import SlugRelatedField
from artelie.models import Brand
from uploader.models import Image
from uploader.serializers import ImageSerializer

class BrandSerializer(serializers.ModelSerializer):
    image_attachment_key = SlugRelatedField(
        source="image",
        queryset=Image.objects.all(),
        slug_field="attachment_key",
        required=False,
        write_only=True,
    )
    image = ImageSerializer(required=False, read_only=True)

    class Meta:
        model = Brand
        fields = '__all__'
        read_only_fields = ['id', 'updated_at']
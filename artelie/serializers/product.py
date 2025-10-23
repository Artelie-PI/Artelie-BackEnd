from rest_framework import serializers
from artelie.models import Product
from rest_framework.serializers import ModelSerializer, SlugRelatedField
from uploader.models import Image
from uploader.serializers import ImageSerializer

class ProductSerializer(serializers.ModelSerializer):
    Image_attachment_key = SlugRelatedField(
        source="Image",
        queryset=Image.objects.all(),
        slug_field="attachment_key",
        required=False,
        write_only=True,
    )
    Image = ImageSerializer(required=False, read_only=True)


    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
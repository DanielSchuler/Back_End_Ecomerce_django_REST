from rest_framework import serializers
from product.models import Product

class ProductSerializer(serializers.ModelSerializer):
    thumbnail = serializers.SerializerMethodField()

    def get_thumbnail(self, product):
        if product.photo:
            return product.photo.url
        return ''

    class Meta:
        model = Product
        fields = '__all__'
        extra_kwargs = {
            'photo': {'required': False},  # Make the 'photo' field optional during updates
        }
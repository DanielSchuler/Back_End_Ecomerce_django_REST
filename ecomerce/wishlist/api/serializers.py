from rest_framework import serializers
from wishlist.models import WishList, WishListItem
from product.api.serializers import ProductSerializer

class WishListItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = WishListItem
        fields = '__all__'

class WishListSerializer(serializers.ModelSerializer):
    wishlist_items = WishListItemSerializer(many=True, read_only=True)

    class Meta:
        model = WishList
        fields = ['user', 'total_items', 'wishlist_items']

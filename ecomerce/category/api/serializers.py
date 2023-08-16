from rest_framework import serializers
from category.models import Category
class CategorySerializer(serializers.ModelSerializer):
    sub_categories = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'sub_categories']

    def get_sub_categories(self, category):
        sub_categories = category.children.all()
        serializer = CategorySerializer(instance=sub_categories, many=True)
        return serializer.data
from rest_framework import permissions

from category.models import Category
from rest_framework import generics
from category.api.serializers import CategorySerializer

class ListCategoriesView(generics.ListAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = CategorySerializer
    queryset = Category.objects.filter(parent__isnull=True)

class ListTopLevelCategoriesView(generics.ListAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = CategorySerializer
    queryset = Category.objects.filter(parent__isnull=True)

    def get_queryset(self):
        return self.queryset
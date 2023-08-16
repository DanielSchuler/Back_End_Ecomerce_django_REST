from rest_framework import generics, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from product.models import Product
from category.models import Category
from .paginations import ProductPagination
from .serializers import ProductSerializer
from django.db.models import Q
from django.utils import timezone


'''
FOR MORE INFORMATION ABOUT WHAT THE VIEWS DO 
SEE VIEW_EXPLANATION.TXT
'''
class ProductDetailView(APIView):
    #permission_classes = (permissions.AllowAny,)

    def get_product(self, product_id):
        try:
            return Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return None

    def validate_product_id(self, productId):
        try:
            product_id = int(productId)
            return product_id
        except ValueError:
            return None

    def handle_invalid_product_id(self):
        return Response(
            {'error': 'Product ID must be an integer'},
            status=status.HTTP_404_NOT_FOUND
        )

    def handle_product_not_found(self):
        return Response(
            {'error': 'Product with this ID does not exist'},
            status=status.HTTP_404_NOT_FOUND
        )

    def get(self, request, productId, format=None):
        product_id = self.validate_product_id(productId)
        if product_id is None:
            return self.handle_invalid_product_id()

        product = self.get_product(product_id)
        if product is None:
            return self.handle_product_not_found()

        serializer = ProductSerializer(product)
        return Response({'product': serializer.data}, status=status.HTTP_200_OK)

    def put(self, request, productId, format=None):
        product_id = self.validate_product_id(productId)
        if product_id is None:
            return self.handle_invalid_product_id()

        product = self.get_product(product_id)
        if product is None:
            return self.handle_product_not_found()

        serializer = ProductSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save(date_updated=timezone.now())
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, productId, format=None):
        product_id = self.validate_product_id(productId)
        if product_id is None:
            return self.handle_invalid_product_id()

        product = self.get_product(product_id)
        if product is None:
            return self.handle_product_not_found()

        product.delete()
        return Response({'success': 'Product deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

class ListProductsView(generics.ListAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    pagination_class = ProductPagination

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        # If no page is specified, return the first page of results
        first_page = self.paginate_queryset(queryset[:self.pagination_class.page_size])
        serializer = self.get_serializer(first_page, many=True)
        if serializer.data:
            return self.get_paginated_response(serializer.data)
        else:
            return Response({'error': 'No products to list'}, status=status.HTTP_404_NOT_FOUND)

class ListSearchView(APIView):
    #permission_classes = (permissions.AllowAny,)
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['date_created']

    def post(self, request, format=None):
        category_id = self._get_category_id(request.data)
        search = self._get_search(request.data)

        queryset = self._get_queryset(search)
        queryset = self._apply_category_filters(queryset, category_id)

        serializer = ProductSerializer(queryset, many=True)
        return Response({'search_products': serializer.data}, status=status.HTTP_200_OK)

    def _get_category_id(self, data):
        try:
            return int(data.get('category_id', 0))
        except ValueError:
            return 0

    def _get_search(self, data):
        return data.get('search', '')

    def _get_queryset(self, search):
        if search:
            return Product.objects.filter(
                Q(description__icontains=search) | Q(name__icontains=search)
            )
        else:
            return Product.objects.all()

    def _apply_category_filters(self, queryset, category_id):
        if category_id != 0:
            category = get_object_or_404(Category, id=category_id)

            if category.parent:
                queryset = queryset.filter(category=category)
            else:
                child_categories = Category.objects.filter(parent=category)

                if not child_categories:
                    queryset = queryset.filter(category=category)
                else:
                    filtered_categories = tuple(child_categories) + (category,)
                    queryset = queryset.filter(category__in=filtered_categories)

        return queryset.order_by('-date_created')


class ListRelatedView(APIView):
    #permission_classes = (permissions.AllowAny,)

    def get(self, request, productId, format=None):
        product_id = self._get_product_id(productId)

        product = get_object_or_404(Product, id=product_id)
        category = product.category

        related_products = self._get_related_products(category)

        if related_products.exists():
            related_products = self._exclude_current_product(related_products, product_id)
            related_products = self._order_by_sold(related_products)

            serializer = ProductSerializer(related_products, many=True)

            if len(serializer.data) > 3:
                return Response({'related_products': serializer.data[:3]}, status=status.HTTP_200_OK)
            elif len(serializer.data) > 0:
                return Response({'related_products': serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'No related products found'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'No related products found'}, status=status.HTTP_200_OK)

    def _get_product_id(self, productId):
        try:
            return int(productId)
        except ValueError:
            return None

    def _get_related_products(self, category):
        if category.parent:
            return Product.objects.filter(category=category)
        else:
            child_categories = Category.objects.filter(parent=category)

            if not child_categories:
                return Product.objects.filter(category=category)

            filtered_categories = tuple(child_categories) + (category,)
            return Product.objects.filter(category__in=filtered_categories)

    def _exclude_current_product(self, related_products, product_id):
        return related_products.exclude(id=product_id)

    def _order_by_sold(self, related_products):
        return related_products.order_by('-sold')

class ListBySearchView(generics.ListAPIView):
    #permission_classes = (permissions.AllowAny,)
    serializer_class = ProductSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['date_created', 'price', 'sold']

    def get_queryset(self):
        queryset = Product.objects.all()

        data = self.request.data
        try:
            category_id = int(data.get('category_id', 0))
        except ValueError:
            return queryset.none()

        price_range = data.get('price_range')


        if category_id != 0:
            if not Category.objects.filter(id=category_id).exists():
                return queryset.none()

            category = Category.objects.get(id=category_id)
            if category.parent:
                queryset = queryset.filter(category=category)
            else:
                if not Category.objects.filter(parent=category).exists():
                    queryset = queryset.filter(category=category)
                else:
                    categories = Category.objects.filter(parent=category)
                    filtered_categories = [category] + list(categories)
                    queryset = queryset.filter(category__in=filtered_categories)

        if price_range == '1 - 19':
            queryset = queryset.filter(price__gte=1, price__lt=20)
        elif price_range == '20 - 39':
            queryset = queryset.filter(price__gte=20, price__lt=40)
        elif price_range == '40 - 59':
            queryset = queryset.filter(price__gte=40, price__lt=60)
        elif price_range == '60 - 79':
            queryset = queryset.filter(price__gte=60, price__lt=80)
        elif price_range == 'More than 80':
            queryset = queryset.filter(price__gte=80)


        return queryset


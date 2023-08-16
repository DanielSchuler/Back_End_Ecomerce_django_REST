from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import filters
from rest_framework.generics import get_object_or_404
from cart.api.serializers import CartItemSerializer
from cart.models import Cart, CartItem
from product.api.serializers import ProductSerializer
from product.models import Product
from django.shortcuts import get_object_or_404
from django.db.models import Sum, F






class CartDetailView(APIView):
    serializer_class = CartItemSerializer
    cart_serializer_class = CartItemSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['product__name']
    ordering_fields = ['product__name', 'product__price']

    def get(self, request, format=None):
        cart_items = self.get_cart_items()
        serialized_cart_items = self.serializer_class(cart_items, many=True)
        return Response({'cart': serialized_cart_items.data}, status=status.HTTP_200_OK)

    def put(self, request, format=None):
        product_id = self.request.data.get('product_id')
        count = self.request.data.get('count')
        product = get_object_or_404(Product, id=product_id)
        cart = self.get_cart()
        cart_item = get_object_or_404(CartItem, cart=cart, product=product)
        if count > product.quantity:
            return Response({'error': 'Not enough of this item in stock'}, status=status.HTTP_200_OK)
        cart_item.count = count
        cart_item.save()
        return self.get(request, format)

    def delete(self, request, format=None):
        product_id = self.request.data.get('product_id')
        product = get_object_or_404(Product, id=product_id)
        cart = self.get_cart()
        cart_item = get_object_or_404(CartItem, cart=cart, product=product)
        cart_item.delete()
        cart_items = self.get_cart_items()
        cart.total_items = cart_items.count()
        cart.save()
        return self.get(request, format)

    def get_cart(self):
        if self.request.user.is_authenticated:
            user = self.request.user
            return get_object_or_404(Cart, user=user)
        else:
            # Return an empty cart
            return Cart.objects.none()

    def get_cart_items(self):
        cart = self.get_cart()
        if cart.exists():
            return CartItem.objects.order_by('product').filter(cart=cart)
        else:
            return CartItem.objects.none()

class GetTotalCartItemsView(APIView):
    def get(self, request, format=None):
        if self.request.user.is_authenticated:
            user = self.request.user

            try:
                cart = Cart.objects.get(user=user)
                total_items = cart.total_items

                return Response(
                    {'total_items': total_items},
                    status=status.HTTP_200_OK)
            except Cart.DoesNotExist:
                # The cart doesn't exist for the authenticated user
                return Response(
                    {'total_items': 0},
                    status=status.HTTP_200_OK)
        else:
            # User is not authenticated, return an empty cart with a message
            return Response(
                {'total_items': 0, 'message': 'Please authenticate to view cart items'},
                status=status.HTTP_200_OK)


class AddItemView(APIView):
    def post(self, request, format=None):
        user = self.request.user
        data = self.request.data

        try:
            product_id = int(data['product_id'])
        except (KeyError, ValueError):
            return Response(
                {'error': 'Product ID must be an integer'},
                status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.filter(id=product_id).first()
            if not product:
                return Response(
                    {'error': 'This product does not exist'},
                    status=status.HTTP_404_NOT_FOUND)

            cart = Cart.objects.get(user=user)

            if CartItem.objects.filter(cart=cart, product=product).exists():
                return Response(
                    {'error': 'Item is already in cart'},
                    status=status.HTTP_409_CONFLICT)

            if product.quantity > 0:
                CartItem.objects.create(
                    product=product, cart=cart, count=1
                )

                total_items = int(cart.total_items) + 1
                Cart.objects.filter(user=user).update(total_items=total_items)

                cart_items = CartItem.objects.order_by('product').filter(cart=cart)
                result = []

                for cart_item in cart_items:
                    item = {}
                    item['id'] = cart_item.id
                    item['count'] = cart_item.count
                    product = Product.objects.get(id=cart_item.product.id)
                    product = ProductSerializer(product)

                    item['product'] = product.data

                    result.append(item)

                return Response({'cart': result}, status=status.HTTP_201_CREATED)
            else:
                return Response(
                    {'error': 'Not enough of this item in stock'},
                    status=status.HTTP_200_OK)
        except Exception:
            return Response(
                {'error': 'Something went wrong when adding item to cart'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

'''
Use Django's annotate and aggregate functions for calculations:
Instead of manually calculating the total cost and total compare cost
using a loop, you can leverage Django's annotate and aggregate functions
to perform calculations directly in the database.
'''
class CartSummaryView(APIView):
    def get(self, request, format=None):
        if not self.request.user.is_authenticated:
            # User is not authenticated, return an empty cart with a message
            return Response(
                {'total_cost': 0, 'total_compare_cost': 0, 'message': 'Please authenticate to view cart summary'},
                status=status.HTTP_200_OK)

        user = self.request.user
        cart = get_object_or_404(Cart, user=user)
        cart_items = CartItem.objects.filter(cart=cart)

        totals = cart_items.aggregate(
            total_cost=Sum(F('product__price') * F('count')),
            total_compare_cost=Sum(F('product__compare_price') * F('count'))
        )
        total_cost = round(totals['total_cost'] or 0, 2)
        total_compare_cost = round(totals['total_compare_cost'] or 0, 2)

        return Response(
            {'total_cost': total_cost, 'total_compare_cost': total_compare_cost},
            status=status.HTTP_200_OK)


class EmptyCartView(APIView):
    def delete(self, request, format=None):
        user = self.request.user

        try:
            cart = Cart.objects.get(user=user)

            cart_items = CartItem.objects.filter(cart=cart)
            if not cart_items.exists():
                return Response(
                    {'success': 'Cart is already empty'},
                    status=status.HTTP_200_OK)

            cart_items.delete()

            # Update cart
            cart.total_items = 0
            cart.save()

            return Response(
                {'success': 'Cart emptied successfully'},
                status=status.HTTP_200_OK)
        except Cart.DoesNotExist:
            return Response(
                {'error': 'Cart does not exist'},
                status=status.HTTP_404_NOT_FOUND)


class SynchCartView(APIView):
    def put(self, request, format=None):
        user = self.request.user
        data = self.request.data

        try:
            cart_items = data.get('cart_items', [])
            cart = get_object_or_404(Cart, user=user)

            # Retrieve product IDs from the cart_items list
            product_ids = [int(item.get('product_id')) for item in cart_items]

            # Retrieve products and quantities
            products = Product.objects.filter(id__in=product_ids).values('id', 'quantity')

            # Create a dictionary with product ID as key and quantity as value
            product_quantity_map = {product['id']: product['quantity'] for product in products}

            # Validate the entire cart_items list
            serializer = CartItemSerializer(data=cart_items, many=True)
            if not serializer.is_valid():
                return Response(
                    {'error': serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Save cart items to the cart
            serializer.save(cart=cart)

            # Update total_items in cart
            total_items = len(cart_items)
            cart.total_items = total_items
            cart.save()

            return Response(
                {'success': 'Cart synchronized'},
                status=status.HTTP_201_CREATED
            )
        except Cart.DoesNotExist:
            return Response(
                {'error': 'Cart does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )

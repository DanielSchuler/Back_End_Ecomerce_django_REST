from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from cart.models import Cart, CartItem
from wishlist.models import WishList, WishListItem
from .serializers import WishListSerializer,WishListItemSerializer
from product.models import Product
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from product.api.serializers import ProductSerializer


class AddItemView(APIView):
    def post(self, request, format=None):
        user = self.request.user
        data = self.request.data

        product_id = data.get('product_id')
        if not product_id:
            return self.error_response('Product ID is required.', status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return self.error_response('This product does not exist.', status.HTTP_404_NOT_FOUND)

        wishlist = WishList.objects.get(user=user)

        if WishListItem.objects.filter(wishlist=wishlist, product=product).exists():
            return self.error_response('Item already in wishlist.', status.HTTP_409_CONFLICT)

        WishListItem.objects.create(product=product, wishlist=wishlist)

        # Update total_items in the wishlist
        wishlist.total_items += 1
        wishlist.save()

        # Delete the item from the cart if it exists
        cart = Cart.objects.get(user=user)
        CartItem.objects.filter(cart=cart, product=product).delete()

        # Update total_items in the cart
        cart.total_items -= 1
        cart.save()

        # Retrieve wishlist items with serialized product data
        wishlist_items = WishListItem.objects.filter(wishlist=wishlist)
        serializer = WishListItemSerializer(wishlist_items, many=True)

        return Response({'wishlist': serializer.data}, status=status.HTTP_201_CREATED)

    def error_response(self, message, status_code):
        return Response({'error': message}, status=status_code)


class GetItemTotalView(APIView):
    def get(self, request, format=None):
        user = self.request.user

        try:
            wishlist = WishList.objects.get(user=user)
            serializer = WishListSerializer(wishlist)
            total_items = serializer.data.get('total_items')

            return Response(
                {'total_items': total_items},
                status=status.HTTP_200_OK
            )
        except WishList.DoesNotExist:
            return Response(
                {'error': 'Wishlist does not exist for the user'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception:
            return Response(
                {'error': 'Something went wrong when retrieving total number of wishlist items'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class WishlistItemDetailView(RetrieveUpdateDestroyAPIView):
    queryset = WishListItem.objects.all()
    serializer_class = WishListItemSerializer
    lookup_field = 'product_id'  # Use 'product_id' as the lookup field

    def get_queryset(self):
        user = self.request.user
        wishlist = WishList.objects.get(user=user)
        return wishlist.wishlist_items.all()

    def put(self, request, *args, **kwargs):
        product_id = kwargs.get('product_id')
        user = self.request.user
        wishlist = WishList.objects.get(user=user)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {'error': 'Product with this ID does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            wishlist_item = WishListItem.objects.get(wishlist=wishlist, product=product)
        except WishListItem.DoesNotExist:
            return Response(
                {'error': 'This product is not in your wishlist'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.get_serializer(wishlist_item, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        if response.status_code == status.HTTP_204_NO_CONTENT:
            # Update total_items in the wishlist
            user = self.request.user
            wishlist = WishList.objects.get(user=user)
            total_items = wishlist.wishlist_items.count()
            wishlist.total_items = total_items
            wishlist.save()
        return response




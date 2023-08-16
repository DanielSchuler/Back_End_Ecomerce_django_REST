from rest_framework.views import APIView
from rest_framework import generics, filters,status
from rest_framework.response import Response
from order.models import Order, OrderItem
from .serializers import OrderSerializer
from rest_framework.exceptions import NotFound

class ListOrdersView(generics.ListAPIView):
    serializer_class = OrderSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['status', 'transaction_id', 'address_line_1']  # Specify the fields you want to enable searching on
    ordering_fields = ['date_issued']  # Specify the fields you want to enable ordering on

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            queryset = Order.objects.filter(user=user).order_by('-date_issued')
            return queryset
        else:
            return []

    def list(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return Response(
                {'detail': 'Authentication credentials were not provided.'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        return super().list(request, *args, **kwargs)




class ListOrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrderSerializer
    queryset = Order.objects.all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['transaction_id']  # Specify the fields you want to enable searching on

    def get_object(self):
        user = self.request.user
        transaction_id = self.kwargs['transactionId']

        try:
            order = Order.objects.get(user=user, transaction_id=transaction_id)
            return order
        except Order.DoesNotExist:
            raise NotFound("Order with this transaction ID does not exist")

    def handle_exception(self, exc):
        if isinstance(exc, NotFound):
            return self.handle_not_found_exception(exc)
        return super().handle_exception(exc)

    def handle_not_found_exception(self, exc):
        response_data = {'error': str(exc)}
        return self.response_class(response_data, status=status.HTTP_404_NOT_FOUND)

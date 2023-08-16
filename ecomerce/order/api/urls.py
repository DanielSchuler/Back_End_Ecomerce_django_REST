from django.urls import path
from django.urls import re_path
from .views import ListOrdersView, ListOrderDetailView

app_name="orders"

urlpatterns = [
    path('get-orders', ListOrdersView.as_view()),
    #path('orders/<str:transactionId>/', ListOrderDetailView.as_view(), name='order-detail'),
    re_path(r'^orders/(?P<transactionId>.+)/$', ListOrderDetailView.as_view(), name='order-detail'),
]
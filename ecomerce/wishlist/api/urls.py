from django.urls import path
from .views import  AddItemView, GetItemTotalView, WishlistItemDetailView

urlpatterns = [

    path('add-item/', AddItemView.as_view()),
    path('get-item-total/', GetItemTotalView.as_view()),

    path('wishlist-item-detail/<int:product_id>/', WishlistItemDetailView.as_view(), name='wishlist-item-detail'),
]
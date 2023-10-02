from django.urls import path
#from .views import CartItemsView, AddItemView, GetTotalView, CartTotalView, UpdateItemView, RemoveItemView, EmptyCartView, SynchCartView
from .views import CartDetailView,GetTotalCartItemsView  , CartSummaryView,AddItemView , EmptyCartView, SynchCartView,test_view
#from .views import   SynchCartView,AddItemView,
urlpatterns = [
    path('cart-detail/', CartDetailView.as_view(), name='cart-detail'),

    path('total-cart-items/', GetTotalCartItemsView.as_view(),name='total-cart-items'),
    path('add-item/', AddItemView.as_view(), name='add-item'),


    path('cart-summary/', CartSummaryView.as_view(),name='cart-summary'),


    path('empty-cart/', EmptyCartView.as_view(),name='empty-cart'),
    path('synch/', SynchCartView.as_view(),name='synch'),
    path('test/', test_view,name='test'),
]
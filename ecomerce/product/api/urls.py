from django.urls import path

from .views import ProductDetailView, ListProductsView, ListSearchView, ListRelatedView, ListBySearchView


app_name="product"
urlpatterns = [
    path('product/<productId>', ProductDetailView.as_view(),name='product-detail'),
    path('list/', ListProductsView.as_view(),name='product-list'),
    path('search/', ListSearchView.as_view(),name='product-search'),
    path('product-related/<productId>', ListRelatedView.as_view(),name='product-related'),
    path('advanced-search/', ListBySearchView.as_view(), name='product-advanced-search'),

]
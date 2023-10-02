from django.urls import path

from .views import ListCategoriesView,ListTopLevelCategoriesView

urlpatterns = [
    path('categories/', ListCategoriesView.as_view(), name='list-all-categories'),
    path('top-level-categories/', ListTopLevelCategoriesView.as_view(), name='list-top-level-categories'),
]
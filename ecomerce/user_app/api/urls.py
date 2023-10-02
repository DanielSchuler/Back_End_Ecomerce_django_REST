from django.urls import path
# from rest_framework.authtoken.views import obtain_auth_token
from .views import registration_view, logout_view, login_view, session_view,MyTokenObtainPairView
#from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.views import (
    #TokenObtainPairView,
    TokenRefreshView,
)




urlpatterns = [
    # metodo generico
    # path('login/',obtain_auth_token, name='login'),
    # vamos a usar el login que creamos
    path('login-app/', login_view, name='login-app'),
    path('register/', registration_view, name='register'),
    path('logout/', logout_view, name='logout'),
    path('session/', session_view, name='session'),
    #path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

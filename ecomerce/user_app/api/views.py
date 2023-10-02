from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from user_app.api.serializers import RegistrationSerializer
from rest_framework.authtoken.models import Token
# from user_app import models
from rest_framework_simplejwt.tokens import RefreshToken

from django.contrib.auth.hashers import check_password
from user_app.models import UserAccount

from django.contrib import auth
from rest_framework.permissions import IsAuthenticated

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    #cambie user por account
    @classmethod
    def get_token(cls, account):
        token = super().get_token(account)
        token['username'] = account.username
        token['email'] = account.email
        token['first_name'] = account.first_name

        return token

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer



# como django en su flujo, cuando un usuario hace una peticion esta es pasada a los views
# en primera instancia, crearemos una funcion que pueda recibir la peticion y llamar
# al serializer para validar los datos de la peticion
@api_view(['POST', ])
def registration_view(request):
   pass

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def session_view(request):
    user = request.user  # This gives you the authenticated user
    data = {
        'status': '200',
        'message': 'Bienvenido',
        'user_id': user.id,
        'username': user.username,
        'email': user.email,
        # Add other user information you want to include in the session response
    }
    return Response(data, status=status.HTTP_200_OK)

@api_view(['POST', ])
def logout_view(request):
   pass


@api_view(['POST'])
def login_view(request):
    data = {}
    data['result'] = {}
    resultado = data['result']

    if request.method == 'POST':
        email = request.data.get('email')
        password = request.data.get('password')

        # Try to authenticate the user
        account = auth.authenticate(email=email, password=password)

        if account is not None:
            data['status'] = '200'
            resultado['response'] = 'El Login fue existoso'
            resultado['username'] = account.username
            resultado['email'] = account.email
            resultado['first_name'] = account.first_name
            resultado['last_name'] = account.last_name
            resultado['phone_number'] = account.phone_number
            refresh = RefreshToken.for_user(account)
            resultado['token'] = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
            return Response(data, status.HTTP_200_OK)
        else:
            # Try to find the user by email to determine if the user doesn't exist
            existing_user = UserAccount.objects.filter(email=email).first()

            if existing_user:
                data['status'] = '401'
                resultado['error'] = 'Credenciales incorrectas: contraseña incorrecta'
            else:
                data['status'] = '404'
                resultado['error'] = 'Credenciales incorrectas: usuario no encontrado'

            return Response(data)
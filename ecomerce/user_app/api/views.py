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


# como django en su flujo, cuando un usuario hace una peticion esta es pasada a los views
# en primera instancia, crearemos una funcion que pueda recibir la peticion y llamar
# al serializer para validar los datos de la peticion
@api_view(['POST', ])
def registration_view(request):
    if request.method == 'POST':
        serializer = RegistrationSerializer(data=request.data)
        data = {}

        if serializer.is_valid():
            account = serializer.save()

            data["response"] = 'El usuario fue registrado exitosamente.'
            data['username'] = account.username
            data['email'] = account.email
            data['first_name'] = account.first_name
            data['last_name'] = account.last_name
            data['phone_number'] = account.phone_number
            # obtener token y asignarlo a un property token
            # token=Token.objects.get(user=account).key
            # data['token']=token

            # se generara el token con el refresh token

            refresh = RefreshToken.for_user(account)
            data['token'] = {
                'refresh': str(refresh),
                'access': str(refresh.access_token)
            }

            # return Response(serializer.data, status = status.HTTP_201_CREATED)
        else:
            data = serializer.errors

        return Response(data)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def session_view(request):
    if request.method == 'GET':
        user = request.user
        account = UserAccount.objects.get(email=user)
        data = {}
        if account is not None:
            data['response'] = 'El usuario esta en sesion'
            data['username'] = account.username
            data['email'] = account.email
            data['first_name'] = account.first_name
            data['last_name'] = account.last_name
            refresh = RefreshToken.for_user(account)
            data['token'] = {
                'refresh': str(refresh),
                'access': str(refresh.access_token)
            }
            return Response(data)
        else:
            data['error'] = 'El usuario no existe'
            return Response(data, status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST', ])
def logout_view(request):
    if request.method == 'POST':
        request.user.auth_token.delete()
        return Response(status=status.HTTP_200_OK)


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
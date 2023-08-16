from rest_framework import serializers
from django.contrib.auth.models import User
# usamos el modelo de cuenta que creamos
from user_app.models import UserAccount


class RegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        #model = User
        # usamos el modelo de cuenta que creamos
        model = UserAccount
        fields = ['username', 'email', 'password', 'password2', 'first_name', 'last_name', 'phone_number']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    # validaciones de los passwors si son iguales

    def save(self):
        password = self.validated_data['password']
        password2 = self.validated_data['password2']

        if password != password2:
            raise serializers.ValidationError({'error': 'Las contraseñas no coinciden'})

            # validacion si el usuario que se esta registrando ya existe

        # if User.objects.filter(email=self.validated_data['email']).exists():
        # usamos el modelo de cuenta que creamos
        if UserAccount.objects.filter(email=self.validated_data['email']).exists():
            raise serializers.ValidationError({'error': 'El email ya esta registrando'})

        # si no ocurre ningun problema se creara la cuenta
        # account = User(email = self.validated_data['email'],
        #                username=self.validated_data['username'])

        # account.set_password(password)
        # usamos el modelo de cuenta que creamos

        account = UserAccount.objects.create_user(first_name=self.validated_data['first_name'],
                                              last_name=self.validated_data['last_name'],
                                              email=self.validated_data['email'],

                                              username=self.validated_data['username'],
                                              password=password)

        account.phone_number = self.validated_data['phone_number']
        account.save()

        return account

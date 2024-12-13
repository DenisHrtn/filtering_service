from rest_framework import status
from rest_framework.response import Response
from decouple import config
from django.db import transaction

from users.models import User
from admin_panel.models import UserData

PROXY_SECRET_KEY = config('PROXY_SECRET_KEY')

KEYS = [
    'user',
    'Email',
    'Endpoint',
    'Login',
    'Message',
    'SupportLevel',
    'Timestamp',
    'UserID',
    'Номер телефона',
    'Имя',
    'Фамилия',
    'Отчество',
    'Пол',
    'Возраст',
    'Дата рождения'
]

FIELDS = [
    'user_id',
    'email',
    'endpoint',
    'login',
    'message',
    'support_level',
    'timestamp',
    'external_user_id',
    'phone_number',
    'name',
    'surname',
    'patronymic',
    'gender',
    'age',
    'birth_date'
]


class SaveUsersDataMixin:
    def create(self, request, *args, **kwargs):
        proxy_secret_key = request.headers.get('X-Proxy-Auth')
        num_of_packet = request.headers.get('X-Num-Of-Packet')
        user_email = request.headers.get('X-UserEmail')

        user = User.objects.filter(email=user_email).first()

        if not user:
            return Response({'error': "User does not exist."}, status=status.HTTP_404_NOT_FOUND)

        if num_of_packet == '1':
            if user_email:
                UserData.objects.filter(user=user).delete()

        if proxy_secret_key != PROXY_SECRET_KEY or not proxy_secret_key:
            return Response({'error': 'Unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)

        data = request.data

        if isinstance(data, list):
            for item in data:
                serializer = self.get_serializer(data=item)
                serializer.is_valid(raise_exception=True)

                user_data_dict = {field: item.get(key, None) for field, key in (FIELDS, KEYS)}

                user_data = UserData(**user_data_dict)
                user_data.user = user

                self.perform_create(serializer)  # saving data using transaction

                return Response({'message': 'Данные успешно сохранены'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'error': 'Неверный формат данных'}, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        with transaction.atomic():
            serializer.dave()

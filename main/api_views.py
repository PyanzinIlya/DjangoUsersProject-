# main/api_views.py
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from django.contrib.auth import authenticate
from .serializers import (
    UserSerializer,
    UserRegisterSerializer,
    UserUpdateSerializer,
    ChangePasswordSerializer,
    UserListSerializer,
    UserDetailSerializer
)


class RegisterAPIView(generics.CreateAPIView):
    """API для регистрации новых пользователей"""
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]  # Доступно всем

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Создаем токен для пользователя
        token, created = Token.objects.get_or_create(user=user)

        return Response({
            'user': UserSerializer(user).data,
            'token': token.key,
            'message': 'Пользователь успешно зарегистрирован'
        }, status=status.HTTP_201_CREATED)


class LoginAPIView(APIView):
    """API для входа в систему"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({
                'error': 'Необходимо указать имя пользователя и пароль'
            }, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'user': UserSerializer(user).data,
                'token': token.key,
                'message': 'Вход выполнен успешно'
            })
        else:
            return Response({
                'error': 'Неверное имя пользователя или пароль'
            }, status=status.HTTP_401_UNAUTHORIZED)


class LogoutAPIView(APIView):
    """API для выхода из системы"""
    permission_classes = [permissions.IsAuthenticated]  # Только для авторизованных

    def post(self, request):
        # Удаляем токен
        request.user.auth_token.delete()
        logout(request)
        return Response({
            'message': 'Выход выполнен успешно'
        })


class UserProfileAPIView(generics.RetrieveUpdateAPIView):
    """API для просмотра и редактирования профиля"""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UserUpdateSerializer
        return UserSerializer


class ChangePasswordAPIView(APIView):
    """API для смены пароля"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            user = request.user

            # Проверяем старый пароль
            if not user.check_password(serializer.validated_data['old_password']):
                return Response({
                    'old_password': 'Неверный текущий пароль'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Устанавливаем новый пароль
            user.set_password(serializer.validated_data['new_password'])
            user.save()

            return Response({
                'message': 'Пароль успешно изменен'
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserListAPIView(generics.ListAPIView):
    """
    API для получения списка всех пользователей (только id и username)
    Доступно всем авторизованным пользователям
    """
    serializer_class = UserListSerializer
    permission_classes = [permissions.IsAuthenticated]  # Только для авторизованных

    def get_queryset(self):
        """Возвращает всех пользователей"""
        return User.objects.all().order_by('id')


class UserDetailAPIView(generics.RetrieveAPIView):
    """
    API для получения детальной информации о пользователе по ID
    Доступно всем авторизованным пользователям
    """
    queryset = User.objects.all()
    serializer_class = UserDetailSerializer
    permission_classes = [permissions.IsAuthenticated]  # Только для авторизованных
    lookup_field = 'id'  # Ищем по полю id
    lookup_url_kwarg = 'user_id'  # В URL параметр будет user_id

class UserListView(generics.ListAPIView):
    """API для получения списка пользователей (только для админов)"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]  # Только для админов
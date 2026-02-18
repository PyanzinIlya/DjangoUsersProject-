# main/api_urls.py
from django.urls import path
from . import api_views

urlpatterns = [
    # Аутентификация
    path('register/', api_views.RegisterAPIView.as_view(), name='api_register'),
    path('login/', api_views.LoginAPIView.as_view(), name='api_login'),
    path('logout/', api_views.LogoutAPIView.as_view(), name='api_logout'),

    # Профиль
    path('profile/', api_views.UserProfileAPIView.as_view(), name='api_profile'),
    path('change-password/', api_views.ChangePasswordAPIView.as_view(), name='api_change_password'),

    # Админские функции
    path('admin/users/', api_views.UserListView.as_view(), name='api_users'),

    path('users/', api_views.UserListAPIView.as_view(), name='api_users_list'),  # Список всех пользователей
    path('users/<int:user_id>/', api_views.UserDetailAPIView.as_view(), name='api_user_detail'),  # Детально по ID
]
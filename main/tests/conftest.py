import pytest
from rest_framework.test import APIClient
from .factories import UserFactory, AdminFactory


@pytest.fixture
def api_client():
    """Фикстура для API клиента"""
    return APIClient()


@pytest.fixture
def authenticated_client(api_client, test_user):
    """Фикстура для авторизованного клиента"""
    # Логиним пользователя через API
    response = api_client.post('/api/login/', {
        'username': test_user.username,
        'password': 'testpass123'
    }, format='json')

    # Проверяем, что логин успешен
    assert response.status_code == 200, f"Login failed: {response.content}"

    token = response.data['token']
    api_client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
    return api_client


@pytest.fixture
def admin_client(api_client, test_admin):
    """Фикстура для авторизованного клиента админа"""
    response = api_client.post('/api/login/', {
        'username': test_admin.username,
        'password': 'testpass123'
    }, format='json')

    assert response.status_code == 200
    token = response.data['token']
    api_client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
    return api_client


@pytest.fixture
def test_user(db):
    """Фикстура для создания тестового пользователя"""
    return UserFactory()


@pytest.fixture
def test_admin(db):
    """Фикстура для создания тестового администратора"""
    return AdminFactory()


@pytest.fixture
def another_user(db):
    """Фикстура для создания другого тестового пользователя"""
    return UserFactory(username='another_user', email='another@example.com')


@pytest.fixture
def user_data():
    """Фикстура с данными для регистрации"""
    return {
        'username': 'newuser',
        'password': 'SecurePass123!',
        'password2': 'SecurePass123!',
        'email': 'newuser@example.com',
        'first_name': 'Новый',
        'last_name': 'Пользователь'
    }
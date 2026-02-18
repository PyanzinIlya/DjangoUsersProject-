import pytest
import allure
from django.contrib.auth.models import User
from rest_framework import status


@pytest.mark.django_db
@allure.feature('Регистрация и авторизация')
class TestAuthAPI:
    """Тесты для API аутентификации"""

    @allure.story('Успешная регистрация')
    @allure.title('Проверка создания нового пользователя')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("Тест проверяет успешную регистрацию нового пользователя с валидными данными")
    def test_register_success(self, api_client, user_data):
        """Тест успешной регистрации"""
        with allure.step("Подготовка данных для регистрации"):
            url = '/api/register/'
            allure.attach(
                str(user_data),
                name="Отправляемые данные",
                attachment_type=allure.attachment_type.JSON
            )

        with allure.step("Отправка POST-запроса на регистрацию"):
            response = api_client.post(url, user_data, format='json')

        with allure.step("Проверка статуса ответа (ожидается 201 Created)"):
            assert response.status_code == status.HTTP_201_CREATED
            allure.attach(
                str(response.status_code),
                name="Статус код",
                attachment_type=allure.attachment_type.TEXT
            )

        with allure.step("Проверка наличия токена в ответе"):
            assert 'token' in response.data
            allure.attach(
                response.data['token'][:20] + "...",
                name="Токен (первые 20 символов)",
                attachment_type=allure.attachment_type.TEXT
            )

        with allure.step("Проверка данных пользователя в ответе"):
            assert response.data['user']['username'] == user_data['username']

        with allure.step("Проверка создания пользователя в базе данных"):
            assert User.objects.filter(username=user_data['username']).exists()
            allure.attach(
                f"Пользователь {user_data['username']} создан в БД",
                name="Результат проверки БД",
                attachment_type=allure.attachment_type.TEXT
            )

    @allure.story('Ошибочная регистрация')
    @allure.title('Регистрация с несовпадающими паролями')
    @allure.severity(allure.severity_level.NORMAL)
    def test_register_password_mismatch(self, api_client, user_data):
        """Тест регистрации с несовпадающими паролями"""
        with allure.step("Модификация данных - изменение второго пароля"):
            original_password2 = user_data.get('password2', '')
            user_data['password2'] = 'differentpass'
            allure.attach(
                f"Оригинальный password2: {original_password2}\n"
                f"Новый password2: differentpass",
                name="Изменения в данных",
                attachment_type=allure.attachment_type.TEXT
            )

        with allure.step("Отправка POST-запроса с несовпадающими паролями"):
            url = '/api/register/'
            response = api_client.post(url, user_data, format='json')

        with allure.step("Проверка статуса ответа (ожидается 400 Bad Request)"):
            assert response.status_code == status.HTTP_400_BAD_REQUEST

        with allure.step("Проверка наличия ошибки валидации пароля"):
            assert 'password' in response.data or any(
                'password' in str(error).lower()
                for error in response.data.values()
            )
            allure.attach(
                str(response.data),
                name="Сообщение об ошибке",
                attachment_type=allure.attachment_type.JSON
            )

        with allure.step("Проверка, что пользователь не создан в БД"):
            assert not User.objects.filter(username=user_data['username']).exists()

    @allure.story('Ошибочная регистрация')
    @allure.title('Регистрация с существующим username')
    @allure.severity(allure.severity_level.CRITICAL)
    def test_register_existing_username(self, api_client, user_data, test_user):
        """Тест регистрации с уже существующим именем пользователя"""
        with allure.step("Подготовка данных с существующим username"):
            old_username = user_data['username']
            user_data['username'] = test_user.username
            allure.attach(
                f"Было: {old_username}\n"
                f"Стало: {test_user.username}",
                name="Изменения в данных",
                attachment_type=allure.attachment_type.TEXT
            )

        with allure.step("Отправка POST-запроса с существующим username"):
            url = '/api/register/'
            response = api_client.post(url, user_data, format='json')

        with allure.step("Проверка статуса ответа (ожидается 400 Bad Request)"):
            assert response.status_code == status.HTTP_400_BAD_REQUEST

        with allure.step("Проверка наличия ошибки валидации username"):
            assert 'username' in response.data
            allure.attach(
                str(response.data['username']),
                name="Ошибка валидации",
                attachment_type=allure.attachment_type.TEXT
            )

    @allure.story('Успешная авторизация')
    @allure.title('Успешный вход в систему')
    @allure.severity(allure.severity_level.CRITICAL)
    def test_login_success(self, api_client, test_user):
        """Тест успешного входа в систему"""
        with allure.step("Подготовка данных для входа"):
            login_data = {
                'username': test_user.username,
                'password': 'testpass123'
            }
            url = '/api/login/'
            allure.attach(
                f"Username: {test_user.username}\nПароль: [СКРЫТ]",
                name="Данные для входа",
                attachment_type=allure.attachment_type.TEXT
            )

        with allure.step("Отправка POST-запроса на вход"):
            response = api_client.post(url, login_data, format='json')

        with allure.step("Проверка статуса ответа (ожидается 200 OK)"):
            assert response.status_code == status.HTTP_200_OK

        with allure.step("Проверка наличия токена в ответе"):
            assert 'token' in response.data
            allure.attach(
                response.data['token'][:20] + "...",
                name="Токен (первые 20 символов)",
                attachment_type=allure.attachment_type.TEXT
            )

        with allure.step("Проверка данных пользователя в ответе"):
            assert response.data['user']['username'] == test_user.username

    @allure.story('Ошибочная авторизация')
    @allure.title('Вход с неверным паролем')
    @allure.severity(allure.severity_level.NORMAL)
    def test_login_wrong_password(self, api_client, test_user):
        """Тест входа с неверным паролем"""
        with allure.step("Подготовка данных с неверным паролем"):
            login_data = {
                'username': test_user.username,
                'password': 'wrongpass'
            }
            url = '/api/login/'
            allure.attach(
                f"Username: {test_user.username}\nПароль: wrongpass (неверный)",
                name="Данные для входа",
                attachment_type=allure.attachment_type.TEXT
            )

        with allure.step("Отправка POST-запроса с неверным паролем"):
            response = api_client.post(url, login_data, format='json')

        with allure.step("Проверка статуса ответа (ожидается 401 Unauthorized)"):
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            allure.attach(
                str(response.data),
                name="Сообщение об ошибке",
                attachment_type=allure.attachment_type.JSON
            )

    @allure.story('Ошибочная авторизация')
    @allure.title('Вход без обязательных полей')
    @allure.severity(allure.severity_level.NORMAL)
    def test_login_missing_fields(self, api_client):
        """Тест входа без обязательных полей"""

        with allure.step("Подготовка пустых данных для входа"):
            url = '/api/login/'
            empty_data = {}
            allure.attach(
                "Отправка пустого тела запроса",
                name="Описание",
                attachment_type=allure.attachment_type.TEXT
            )

        with allure.step("Отправка POST-запроса с пустыми данными"):
            response = api_client.post(url, empty_data, format='json')

        with allure.step("Проверка статуса ответа (ожидается 400 Bad Request)"):
            assert response.status_code == status.HTTP_400_BAD_REQUEST

        with allure.step("Проверка наличия ошибки валидации"):
            # Проверяем, что есть поле 'error' с нужным текстом
            assert 'error' in response.data
            assert response.data['error'] == 'Необходимо указать имя пользователя и пароль'
            allure.attach(
                str(response.data),
                name="Ошибка валидации",
                attachment_type=allure.attachment_type.JSON
            )

    @allure.story('Успешный выход')
    @allure.title('Успешный выход из системы')
    @allure.severity(allure.severity_level.NORMAL)
    def test_logout_success(self, authenticated_client):
        """Тест успешного выхода из системы"""
        with allure.step("Подготовка к выходу из системы"):
            url = '/api/logout/'
            allure.attach(
                "Используется аутентифицированный клиент",
                name="Предусловия",
                attachment_type=allure.attachment_type.TEXT
            )

        with allure.step("Отправка POST-запроса на выход"):
            response = authenticated_client.post(url)

        with allure.step("Проверка статуса ответа (ожидается 200 OK)"):
            assert response.status_code == status.HTTP_200_OK

        with allure.step("Проверка сообщения об успешном выходе"):
            assert response.data['message'] == 'Выход выполнен успешно'
            allure.attach(
                response.data['message'],
                name="Сообщение",
                attachment_type=allure.attachment_type.TEXT
            )

    @allure.story('Ошибочный выход')
    @allure.title('Выход без авторизации')
    @allure.severity(allure.severity_level.NORMAL)
    def test_logout_without_auth(self, api_client):
        """Тест выхода без предварительной авторизации"""
        with allure.step("Подготовка неаутентифицированного запроса"):
            url = '/api/logout/'
            allure.attach(
                "Используется неаутентифицированный клиент",
                name="Предусловия",
                attachment_type=allure.attachment_type.TEXT
            )

        with allure.step("Отправка POST-запроса на выход без токена"):
            response = api_client.post(url)

        with allure.step("Проверка статуса ответа (ожидается 401 Unauthorized)"):
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            allure.attach(
                str(response.data),
                name="Сообщение об ошибке",
                attachment_type=allure.attachment_type.JSON
            )
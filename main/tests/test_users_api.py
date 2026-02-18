import pytest
import allure
from rest_framework import status


@pytest.mark.django_db
@allure.feature('API пользователей')
class TestUsersAPI:
    """Тесты для API пользователей"""

    @allure.story('Список пользователей')
    @allure.title('Успешное получение списка пользователей')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("""
        Тест проверяет получение списка всех пользователей.

        Ожидаемый результат:
        - Статус 200 OK
        - Список содержит минимум 2 пользователей
        - В ответе только id и username
    """)
    def test_users_list_success(self, authenticated_client, test_user, another_user):
        with allure.step("Подготовка к запросу списка пользователей"):
            url = '/api/users/'
            allure.attach(
                f"URL: {url}\n"
                f"Авторизованный пользователь: {test_user.username}\n"
                f"Ожидаемое количество пользователей: минимум 2",
                name="Параметры запроса",
                attachment_type=allure.attachment_type.TEXT
            )

        with allure.step("Отправка GET-запроса на получение списка пользователей"):
            response = authenticated_client.get(url)
            allure.attach(
                f"Статус ответа: {response.status_code}",
                name="Информация о запросе",
                attachment_type=allure.attachment_type.TEXT
            )

        with allure.step("Проверка статуса ответа (ожидается 200 OK)"):
            assert response.status_code == status.HTTP_200_OK, \
                f"Ожидался 200, получен {response.status_code}"

        with allure.step("Проверка количества пользователей в списке"):
            users_count = len(response.data)
            assert users_count >= 2, \
                f"Ожидалось минимум 2 пользователя, получено {users_count}"
            allure.attach(
                f"Найдено пользователей: {users_count}",
                name="Количество пользователей",
                attachment_type=allure.attachment_type.TEXT
            )

        with allure.step("Проверка структуры данных пользователя"):
            if len(response.data) > 0:
                first_user = response.data[0]
                actual_fields = set(first_user.keys())
                expected_fields = {'id', 'username'}

                assert actual_fields == expected_fields, \
                    f"Неверные поля в ответе: ожидались {expected_fields}, получены {actual_fields}"

                allure.attach(
                    f"Поля пользователя: {actual_fields}",
                    name="Структура данных",
                    attachment_type=allure.attachment_type.TEXT
                )

    @allure.story('Список пользователей')
    @allure.title('Попытка получения списка пользователей без авторизации')
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("""
        Тест проверяет, что неавторизованный пользователь
        не может получить список пользователей.

        Ожидаемый результат:
        - Статус 401 Unauthorized
    """)
    def test_users_list_unauthorized(self, api_client):
        with allure.step("Подготовка запроса без авторизации"):
            url = '/api/users/'
            allure.attach(
                f"URL: {url}\nТокен: отсутствует",
                name="Параметры запроса",
                attachment_type=allure.attachment_type.TEXT
            )

        with allure.step("Отправка GET-запроса без токена авторизации"):
            response = api_client.get(url)

        with allure.step("Проверка статуса ответа (ожидается 401 Unauthorized)"):
            assert response.status_code == status.HTTP_401_UNAUTHORIZED, \
                f"Ожидался 401, получен {response.status_code}"

            allure.attach(
                str(response.data),
                name="Сообщение об ошибке",
                attachment_type=allure.attachment_type.JSON
            )

    @allure.story('Детальная информация о пользователе')
    @allure.title('Успешное получение детальной информации о пользователе')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("""
        Тест проверяет получение детальной информации
        о конкретном пользователе.

        Ожидаемый результат:
        - Статус 200 OK
        - Все поля пользователя присутствуют в ответе
    """)
    def test_user_detail_success(self, authenticated_client, test_user, another_user):
        with allure.step("Подготовка к запросу детальной информации"):
            url = f'/api/users/{another_user.id}/'
            allure.attach(
                f"URL: {url}\n"
                f"Запрашиваемый пользователь: {another_user.username} (ID: {another_user.id})\n"
                f"Авторизованный пользователь: {test_user.username}",
                name="Параметры запроса",
                attachment_type=allure.attachment_type.TEXT
            )

        with allure.step("Отправка GET-запроса на получение детальной информации"):
            response = authenticated_client.get(url)
            allure.attach(
                f"Статус ответа: {response.status_code}",
                name="Информация о запросе",
                attachment_type=allure.attachment_type.TEXT
            )

        with allure.step("Проверка статуса ответа (ожидается 200 OK)"):
            assert response.status_code == status.HTTP_200_OK, \
                f"Ожидался 200, получен {response.status_code}"

        with allure.step("Проверка ID пользователя"):
            assert response.data['id'] == another_user.id, \
                f"Неверный ID: ожидался {another_user.id}, получен {response.data['id']}"

        with allure.step("Проверка username пользователя"):
            assert response.data['username'] == another_user.username, \
                f"Неверный username: ожидался {another_user.username}, получен {response.data['username']}"

        with allure.step("Проверка email пользователя"):
            assert response.data['email'] == another_user.email, \
                f"Неверный email: ожидался {another_user.email}, получен {response.data['email']}"

        with allure.step("Проверка наличия обязательных полей"):
            expected_fields = {'id', 'username', 'email', 'first_name', 'last_name', 'date_joined', 'last_login'}
            actual_fields = set(response.data.keys())

            missing_fields = expected_fields - actual_fields
            assert not missing_fields, f"Отсутствуют поля: {missing_fields}"

            allure.attach(
                f"Все поля присутствуют: {actual_fields}",
                name="Структура данных",
                attachment_type=allure.attachment_type.TEXT
            )

    @allure.story('Детальная информация о пользователе')
    @allure.title('Попытка получения информации о несуществующем пользователе')
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("""
        Тест проверяет, что при запросе несуществующего пользователя
        возвращается ошибка 404.

        Ожидаемый результат:
        - Статус 404 Not Found
    """)
    def test_user_detail_not_found(self, authenticated_client):
        with allure.step("Подготовка запроса с несуществующим ID"):
            non_existent_id = 99999
            url = f'/api/users/{non_existent_id}/'
            allure.attach(
                f"URL: {url}\n"
                f"Запрашиваемый ID: {non_existent_id} (не существует)",
                name="Параметры запроса",
                attachment_type=allure.attachment_type.TEXT
            )

        with allure.step("Отправка GET-запроса на получение несуществующего пользователя"):
            response = authenticated_client.get(url)

        with allure.step("Проверка статуса ответа (ожидается 404 Not Found)"):
            assert response.status_code == status.HTTP_404_NOT_FOUND, \
                f"Ожидался 404, получен {response.status_code}"

            allure.attach(
                str(response.data),
                name="Сообщение об ошибке",
                attachment_type=allure.attachment_type.JSON
            )

    @allure.story('Административные функции')
    @allure.title('Успешное получение админского списка пользователей')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("""
        Тест проверяет, что администратор может получить
        расширенный список пользователей со всеми полями.

        Ожидаемый результат:
        - Статус 200 OK
        - В ответе присутствуют все поля пользователя
    """)
    def test_admin_users_list_success(self, api_client, test_admin):
        with allure.step("Авторизация администратора"):
            login_data = {
                'username': test_admin.username,
                'password': 'testpass123'
            }
            login_response = api_client.post('/api/login/', login_data, format='json')

            assert login_response.status_code == status.HTTP_200_OK, \
                "Не удалось авторизоваться как администратор"

            token = login_response.data['token']
            allure.attach(
                f"Администратор: {test_admin.username}\n"
                f"Токен получен: {token[:20]}...",
                name="Авторизация администратора",
                attachment_type=allure.attachment_type.TEXT
            )

        with allure.step("Настройка клиента с токеном администратора"):
            admin_client = api_client
            admin_client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
            url = '/api/admin/users/'

            allure.attach(
                f"URL: {url}\n"
                f"Заголовок Authorization: Token {token[:20]}...",
                name="Параметры запроса",
                attachment_type=allure.attachment_type.TEXT
            )

        with allure.step("Отправка GET-запроса на получение админского списка"):
            response = admin_client.get(url)

        with allure.step("Проверка статуса ответа (ожидается 200 OK)"):
            assert response.status_code == status.HTTP_200_OK, \
                f"Ожидался 200, получен {response.status_code}"

        with allure.step("Проверка структуры данных пользователя"):
            if len(response.data) > 0:
                first_user = response.data[0]
                actual_fields = set(first_user.keys())

                expected_fields = {'id', 'username', 'email', 'first_name', 'last_name', 'date_joined', 'last_login'}
                assert actual_fields.issuperset(expected_fields), \
                    f"Не все обязательные поля присутствуют: {actual_fields}"

                missing_fields = expected_fields - actual_fields
                if missing_fields:
                    allure.attach(
                        f"Отсутствуют поля: {missing_fields}",
                        name="Предупреждение",
                        attachment_type=allure.attachment_type.TEXT
                    )
                else:
                    allure.attach(
                        f"Все поля присутствуют: {actual_fields}",
                        name="Структура данных",
                        attachment_type=allure.attachment_type.TEXT
                    )

    @allure.story('Административные функции')
    @allure.title('Попытка доступа к админскому списку обычным пользователем')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("""
        Тест проверяет, что обычный пользователь
        не может получить админский список пользователей.

        Ожидаемый результат:
        - Статус 403 Forbidden
    """)
    def test_admin_users_list_forbidden(self, authenticated_client, test_user):
        with allure.step("Подготовка запроса от обычного пользователя"):
            url = '/api/admin/users/'
            allure.attach(
                f"URL: {url}\n"
                f"Пользователь: {test_user.username} (обычный пользователь, не админ)",
                name="Параметры запроса",
                attachment_type=allure.attachment_type.TEXT
            )

        with allure.step("Отправка GET-запроса на админский список"):
            response = authenticated_client.get(url)

        with allure.step("Проверка статуса ответа (ожидается 403 Forbidden)"):
            assert response.status_code == status.HTTP_403_FORBIDDEN, \
                f"Ожидался 403, получен {response.status_code}"

            allure.attach(
                str(response.data),
                name="Сообщение об ошибке",
                attachment_type=allure.attachment_type.JSON
            )
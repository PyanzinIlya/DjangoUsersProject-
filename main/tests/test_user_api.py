import pytest
import allure
from rest_framework import status


@pytest.mark.django_db
@allure.feature('Профиль пользователя')
class TestProfileAPI:

    @allure.story('Получение профиля')
    @allure.title('Успешное получение профиля авторизованным пользователем')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("""
        Тест проверяет успешное получение данных профиля
        авторизованным пользователем.

        Ожидаемый результат:
        - Статус 200 OK
        - Данные пользователя соответствуют БД
    """)
    def test_get_profile_success(self, authenticated_client, test_user):
        with allure.step("Подготовка к запросу профиля"):
            url = '/api/profile/'
            allure.attach(
                f"Пользователь: {test_user.username}\nURL: {url}",
                name="Параметры запроса",
                attachment_type=allure.attachment_type.TEXT
            )

        with allure.step("Отправка GET-запроса на получение профиля"):
            response = authenticated_client.get(url)
            allure.attach(
                f"Статус ответа: {response.status_code}",
                name="Информация о запросе",
                attachment_type=allure.attachment_type.TEXT
            )

        with allure.step("Проверка статуса ответа (ожидается 200 OK)"):
            assert response.status_code == status.HTTP_200_OK, \
                f"Ожидался 200, получен {response.status_code}"

        with allure.step("Проверка соответствия username"):
            assert response.data['username'] == test_user.username, \
                f"Неверный username: ожидался {test_user.username}, получен {response.data['username']}"

        with allure.step("Проверка соответствия email"):
            assert response.data['email'] == test_user.email, \
                f"Неверный email: ожидался {test_user.email}, получен {response.data['email']}"

        with allure.step("Проверка наличия обязательных полей в ответе"):
            expected_fields = ['id', 'username', 'email', 'first_name', 'last_name']
            for field in expected_fields:
                assert field in response.data, f"В ответе отсутствует поле '{field}'"

            allure.attach(
                f"Все поля присутствуют: {list(response.data.keys())}",
                name="Поля ответа",
                attachment_type=allure.attachment_type.TEXT
            )

    @allure.story('Получение профиля')
    @allure.title('Попытка получения профиля без авторизации')
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("""
        Тест проверяет, что неавторизованный пользователь
        не может получить данные профиля.

        Ожидаемый результат:
        - Статус 401 Unauthorized
    """)
    def test_get_profile_unauthorized(self, api_client):
        with allure.step("Подготовка запроса без авторизации"):
            url = '/api/profile/'
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

    @allure.story('Обновление профиля')
    @allure.title('Успешное обновление профиля')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("""
        Тест проверяет успешное обновление данных профиля.

        Ожидаемый результат:
        - Статус 200 OK
        - Данные обновляются в ответе и в БД
    """)
    def test_update_profile_success(self, authenticated_client, test_user):
        with allure.step("Подготовка данных для обновления"):
            url = '/api/profile/'
            new_data = {
                'email': 'newemail@example.com',
                'first_name': 'Обновленное',
                'last_name': 'Имя'
            }
            allure.attach(
                str(new_data),
                name="Данные для обновления",
                attachment_type=allure.attachment_type.JSON
            )

            # Сохраняем старые данные для сравнения
            old_email = test_user.email
            old_first_name = test_user.first_name

        with allure.step("Отправка PATCH-запроса на обновление профиля"):
            response = authenticated_client.patch(url, new_data, format='json')
            allure.attach(
                f"Статус ответа: {response.status_code}",
                name="Информация о запросе",
                attachment_type=allure.attachment_type.TEXT
            )

        with allure.step("Проверка статуса ответа (ожидается 200 OK)"):
            assert response.status_code == status.HTTP_200_OK, \
                f"Ожидался 200, получен {response.status_code}"

        with allure.step("Проверка обновленного email в ответе"):
            assert response.data['email'] == new_data['email'], \
                f"Email не обновился: ожидался {new_data['email']}, получен {response.data['email']}"

        with allure.step("Проверка обновленного first_name в ответе"):
            assert response.data['first_name'] == new_data['first_name'], \
                f"first_name не обновился: ожидался {new_data['first_name']}, получен {response.data['first_name']}"

        with allure.step("Проверка обновления данных в базе данных"):
            test_user.refresh_from_db()
            assert test_user.email == new_data['email'], "Email не обновился в БД"
            assert test_user.first_name == new_data['first_name'], "first_name не обновился в БД"

            allure.attach(
                f"Было: email={old_email}, first_name={old_first_name}\n"
                f"Стало: email={test_user.email}, first_name={test_user.first_name}",
                name="Изменения в БД",
                attachment_type=allure.attachment_type.TEXT
            )

    @allure.story('Обновление профиля')
    @allure.title('Попытка обновления с уже существующим email')
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("""
        Тест проверяет, что нельзя установить email,
        который уже используется другим пользователем.

        Ожидаемый результат:
        - Статус 400 Bad Request
        - Сообщение об ошибке
    """)
    def test_update_profile_email_exists(self, authenticated_client, another_user, test_user):
        with allure.step("Подготовка данных с существующим email"):
            url = '/api/profile/'
            update_data = {
                'email': another_user.email
            }
            allure.attach(
                f"Попытка установить email: {another_user.email}\n"
                f"Владелец email: {another_user.username}\n"
                f"Текущий пользователь: {test_user.username}",
                name="Данные для обновления",
                attachment_type=allure.attachment_type.TEXT
            )

        with allure.step("Отправка PATCH-запроса с существующим email"):
            response = authenticated_client.patch(url, update_data, format='json')

        with allure.step("Проверка статуса ответа (ожидается 400 Bad Request)"):
            assert response.status_code == status.HTTP_400_BAD_REQUEST, \
                f"Ожидался 400, получен {response.status_code}"

        with allure.step("Проверка наличия ошибки валидации email"):
            assert 'email' in response.data or any('email' in str(error).lower() for error in response.data.values()), \
                "В ответе нет ошибки, связанной с email"

            allure.attach(
                str(response.data),
                name="Сообщение об ошибке",
                attachment_type=allure.attachment_type.JSON
            )

        with allure.step("Проверка, что email не изменился в БД"):
            test_user.refresh_from_db()
            assert test_user.email != another_user.email, "Email изменился в БД, хотя не должен"
            allure.attach(
                f"Email остался: {test_user.email}",
                name="Проверка БД",
                attachment_type=allure.attachment_type.TEXT
            )

    @allure.story('Смена пароля')
    @allure.title('Успешная смена пароля')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("""
        Тест проверяет успешную смену пароля пользователя.

        Ожидаемый результат:
        - Статус 200 OK
        - Сообщение об успешной смене пароля
    """)
    def test_change_password_success(self, authenticated_client, test_user):
        with allure.step("Подготовка данных для смены пароля"):
            url = '/api/change-password/'
            password_data = {
                'old_password': 'testpass123',
                'new_password': 'newpass123',
                'new_password2': 'newpass123'
            }
            allure.attach(
                "old_password: testpass123\n"
                "new_password: newpass123\n"
                "new_password2: newpass123",
                name="Данные для смены пароля",
                attachment_type=allure.attachment_type.TEXT
            )

        with allure.step("Отправка POST-запроса на смену пароля"):
            response = authenticated_client.post(url, password_data, format='json')

        with allure.step("Проверка статуса ответа (ожидается 200 OK)"):
            assert response.status_code == status.HTTP_200_OK, \
                f"Ожидался 200, получен {response.status_code}"

        with allure.step("Проверка сообщения об успешной смене пароля"):
            assert response.data['message'] == 'Пароль успешно изменен', \
                f"Неверное сообщение: {response.data.get('message')}"

            allure.attach(
                response.data['message'],
                name="Сообщение",
                attachment_type=allure.attachment_type.TEXT
            )

        with allure.step("Проверка возможности входа с новым паролем"):
            # Пытаемся войти с новым паролем (необязательно, но полезно)
            login_url = '/api/login/'
            login_response = authenticated_client.post(login_url, {
                'username': test_user.username,
                'password': 'newpass123'
            }, format='json')

            if login_response.status_code == status.HTTP_200_OK:
                allure.attach(
                    "Вход с новым паролем выполнен успешно",
                    name="Дополнительная проверка",
                    attachment_type=allure.attachment_type.TEXT
                )

    @allure.story('Смена пароля')
    @allure.title('Смена пароля с неверным старым паролем')
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("""
        Тест проверяет, что нельзя сменить пароль
        без указания верного старого пароля.

        Ожидаемый результат:
        - Статус 400 Bad Request
        - Сообщение об ошибке
    """)
    def test_change_password_wrong_old(self, authenticated_client):
        with allure.step("Подготовка данных с неверным старым паролем"):
            url = '/api/change-password/'
            password_data = {
                'old_password': 'wrongpass',
                'new_password': 'newpass123',
                'new_password2': 'newpass123'
            }
            allure.attach(
                "old_password: wrongpass (неверный)\n"
                "new_password: newpass123\n"
                "new_password2: newpass123",
                name="Данные для смены пароля",
                attachment_type=allure.attachment_type.TEXT
            )

        with allure.step("Отправка POST-запроса с неверным старым паролем"):
            response = authenticated_client.post(url, password_data, format='json')

        with allure.step("Проверка статуса ответа (ожидается 400 Bad Request)"):
            assert response.status_code == status.HTTP_400_BAD_REQUEST, \
                f"Ожидался 400, получен {response.status_code}"

        with allure.step("Проверка наличия ошибки"):
            error_field = 'old_password' if 'old_password' in response.data else 'error'
            assert error_field in response.data, "В ответе нет информации об ошибке"

            allure.attach(
                str(response.data),
                name="Сообщение об ошибке",
                attachment_type=allure.attachment_type.JSON
            )

    @allure.story('Смена пароля')
    @allure.title('Смена пароля с несовпадающими новыми паролями')
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("""
        Тест проверяет, что новые пароли должны совпадать.

        Ожидаемый результат:
        - Статус 400 Bad Request
        - Сообщение об ошибке в поле new_password
    """)
    def test_change_password_mismatch(self, authenticated_client):
        with allure.step("Подготовка данных с несовпадающими новыми паролями"):
            url = '/api/change-password/'
            password_data = {
                'old_password': 'testpass123',
                'new_password': 'newpass123',
                'new_password2': 'different'
            }
            allure.attach(
                "old_password: testpass123\n"
                "new_password: newpass123\n"
                "new_password2: different (не совпадает)",
                name="Данные для смены пароля",
                attachment_type=allure.attachment_type.TEXT
            )

        with allure.step("Отправка POST-запроса с несовпадающими новыми паролями"):
            response = authenticated_client.post(url, password_data, format='json')

        with allure.step("Проверка статуса ответа (ожидается 400 Bad Request)"):
            assert response.status_code == status.HTTP_400_BAD_REQUEST, \
                f"Ожидался 400, получен {response.status_code}"

        with allure.step("Проверка наличия ошибки в поле new_password"):
            assert 'new_password' in response.data, \
                f"В ответе нет поля 'new_password': {response.data}"

            error_messages = response.data['new_password']
            assert any('не совпадают' in msg.lower() for msg in error_messages), \
                f"В поле new_password нет сообщения о несовпадении: {error_messages}"

            allure.attach(
                str(error_messages),
                name="Сообщение об ошибке",
                attachment_type=allure.attachment_type.JSON
            )
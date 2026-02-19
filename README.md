# DjangoUsersProject

Проект на Django с тестированием и Allure отчетами.

## 🚀 Быстрый старт

### Предварительные требования
- Python 3.9+
- Git
- (Опционально) Allure Commandline для отчетов

### Установка

1. **Клонируйте репозиторий**
   ```bash
   git clone https://github.com/PyanzinIlya/DjangoUsersProject-.git
   cd DjangoUsersProject-


### 2. Создайте виртуальное окружение

Windows:

bash
python -m venv venv
venv\Scripts\activate

Mac/Linux:

bash
python3 -m venv venv
source venv/bin/activate

### 3. Установите зависимости

bash
pip install -r requirements.txt

### 4.Настройте переменные окружения

bash
cp .env.example .env
Отредактируйте .env файл, добавьте свой SECRET_KEY

### 5. Примените миграции

bash
python manage.py migrate
Создайте суперпользователя

bash
python manage.py createsuperuser

### 6.Запустите сервер

bash
python manage.py runserver
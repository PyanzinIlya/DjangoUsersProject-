# DjangoUsersProject
Проект на Django с тестированием и Allure отчетами.


# Запуск прокета на джанго
python manage.py runserver  

# Запуск всех тестов
pytest

# Запуск тестов с Allure отчетом
pytest --alluredir=allure-results
allure serve allure-results


# Полезные команды Git
# Проверить статус файлов
git status

# Посмотреть историю коммитов
git log --oneline

# Создать новую ветку
git checkout -b feature/new-feature

# Обновить локальный репозиторий
git pull origin main

# Отменить изменения в файле
git checkout -- filename.py

# Добавить изменения
git add .

# Сделать коммит
git commit -m "Описание изменений"

# Отправить на GitHub
git push
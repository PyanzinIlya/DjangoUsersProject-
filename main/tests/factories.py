import factory
from django.contrib.auth.models import User


class UserFactory(factory.django.DjangoModelFactory):
    """Фабрика для создания тестовых пользователей"""

    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'testuser{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    is_active = True


class AdminFactory(UserFactory):
    """Фабрика для создания администраторов"""
    is_staff = True
    is_superuser = True


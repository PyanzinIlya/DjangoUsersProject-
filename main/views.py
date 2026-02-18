from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import SignUpForm, UserUpdateForm


def home(request):
    return render(request, 'home.html')
@login_required
def about(request):
    return render(request, 'about.html')


def sign_up(request):
    if request.method == 'POST':
        # Если форма отправлена, передаем в нее данные из POST-запроса
        form = SignUpForm(request.POST)
        if form.is_valid():
            # Сохраняем нового пользователя
            user = form.save()
            # Сразу логиним пользователя после регистрации
            login(request, user)
            # Перенаправляем на главную страницу или в личный кабинет
            return redirect('home')  # 'home' - имя вашего главного URL
    else:
        # Если страница просто открыта (GET-запрос), показываем пустую форму
        form = SignUpForm()

    # Передаем форму в шаблон
    return render(request, 'registration/sign_up.html', {'form': form})


@login_required  # Только авторизованные пользователи могут зайти
def profile(request):
    """Профиль пользователя"""
    if request.method == 'POST':
        # Если форма отправлена, обрабатываем данные
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ваш профиль успешно обновлен!')
            return redirect('profile')
    else:
        # Если просто открыта страница, показываем форму с текущими данными
        form = UserUpdateForm(instance=request.user)

    return render(request, 'profile.html', {'form': form})
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from .models import AuthToken, Profile
from django.conf import settings


class MyUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        fields = ['username', 'password1', 'password2',
                  'first_name', 'last_name', 'email']

    def save(self, commit=True):
        if settings.ACTIVATE_USERS_EMAIL:
            user: AbstractUser = super().save(commit=False)
            user.is_active = False
            if commit:
                user.save()
                token = self.create_token(user)
                self.send_email(user, token)
        else:
            user = super().save(commit=commit)
            Profile.objects.create(user=user)
        return user

    def create_token(self, user):
        return AuthToken.objects.create(user=user)

    def send_email(self, user, token):
        if user.email:
            subject = 'Вы создали учётную запись на сайте "Мой Блог"'
            link = settings.BASE_HOST + reverse('accounts:activate', kwargs={'token': token.token})
            message = f'''Здравствуйте, {user.username}!
Вы создали учётную запись на сайте "Мой Блог"
Активируйте её, перейдя по ссылке {link}.
Если вы считаете, что это ошибка, просто игнорируйте это письмо.'''
            html_message = f'''Здравствуйте, {user.username}!
Вы создали учётную запись на сайте "Мой Блог"
Активируйте её, перейдя по ссылке <a href="{link}">{link}</a>.
Если вы считаете, что это ошибка, просто игнорируйте это письмо.'''
            try:
                user.email_user(subject, message, html_message=html_message)
            except Exception as e:
                print(e)

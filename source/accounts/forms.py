from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class MyUserCreationForm(UserCreationForm):

    email = forms.EmailField(required=True)

    def clean(self):
        cleaned_data = super(MyUserCreationForm, self).clean()
        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')

        if not(first_name or last_name):
            raise ValidationError('Enter either first or last name!!!')

        return cleaned_data

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2',
                  'first_name', 'last_name', 'email']

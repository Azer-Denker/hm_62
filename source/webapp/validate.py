from django.core.exceptions import ValidationError


def title(string):
    if not string[0].isupper():
        raise ValidationError('Это поле надо заплонять с заглавной буквы')


def null(string):
    if str(0) in string:
        raise ValidationError("Нулевые символы не допускаются.")

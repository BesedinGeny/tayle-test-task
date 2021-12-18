from django.conf import settings
from django.core.validators import BaseValidator
from django.db import models

# Create your models here.


class MinValueValidator(BaseValidator):
    message = 'Ensure this value is greater than or equal to %(limit_value)s.'
    code = 'min_value'

    def compare(self, a, b):
        return a < b  # super simple.


class Balance(models.Model):
    sum = models.FloatField(validators=[MinValueValidator(0)])  # сделать проверку при сохранении, чтобы баланс не был < 0
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username + ": " + str(self.sum)
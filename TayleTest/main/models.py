from django.conf import settings
from django.core.validators import BaseValidator
from django.db import models


class MinValueValidator(BaseValidator):
    message = 'Ensure this value is greater than or equal to %(limit_value)s.'
    code = 'min_value'

    def compare(self, a, b):
        return a < b


class Balance(models.Model):
    """Счет пользователя"""
    name = models.CharField(max_length=128, default='New Balance')
    sum = models.FloatField(validators=[MinValueValidator(0)])
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username + ": " + self.name + ", " + str(self.sum)


class Transaction(models.Model):
    """Проведенная операция перевода средств"""
    balance_to = models.ForeignKey(Balance, on_delete=models.CASCADE, blank=False,
                                   related_name='%(class)s_balance_to')  # счет зачисления
    balances_from = models.ManyToManyField(Balance, blank=False,
                                           related_name='%(class)s_balances_from')  # счета списания
    sum = models.FloatField(validators=[MinValueValidator(0)])  # денег переведено

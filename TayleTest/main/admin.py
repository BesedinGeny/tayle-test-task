from django.contrib import admin

# Register your models here.
from .models import Balance, Transaction

admin.site.register(Balance)
admin.site.register(Transaction)
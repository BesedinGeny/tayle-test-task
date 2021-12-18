from django.urls import path
from .views import *

urlpatterns = [
    path('', base, name='base'),
    path('accounts/registration', registration_view, name='register'),
    path('accounts/login/', login_view, name='login'),
]

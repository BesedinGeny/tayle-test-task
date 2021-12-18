from django.urls import path
from .views import *

urlpatterns = [
    path('', base, name='base'),
    path('users_list', UserList.as_view(), name='user_list'),
    path('transaction_list', TransactionList.as_view(), name='transaction_list'),
    path('make_transaction/<respond_to>', make_transaction, name='make_transaction'),
    path('accounts/registration', registration_view, name='register'),
    path('accounts/login/', login_view, name='login'),
]

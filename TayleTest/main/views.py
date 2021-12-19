from itertools import islice, chain

from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import RegistrationForm, LoginForm, MakeTransaction
from .models import Balance, Transaction


def base(request):
    balances = Balance.objects.filter(user__username=request.user.username)
    return render(request, 'main/base.html', context={
        'current_user': request.user.username,
        'balances': balances
    })


@login_required()
def make_transaction(request, respond_to):
    context = {}
    user_to = get_object_or_404(User, username=respond_to)
    user_from = get_object_or_404(User, username=request.user.username)
    balances_to = Balance.objects.filter(user__username=respond_to)
    balances_from = Balance.objects.filter(user__username=user_from.username)
    context['current_user'] = user_from.username
    context['user_to'] = user_to
    context['balances_to'] = balances_to
    context['balances_from'] = balances_from
    if request.POST:
        form = MakeTransaction(request.POST)
        if form.is_valid():
            # TODO: хорошо бы вынести логику в controller -_-
            post_data = dict(request.POST)
            if post_data['sum'][0] < 0:  # валидация на положительное число
                context['error'] = 'Sum must has positive value'
                return render(request, 'main/transaction.html', context=context)
            # создаем транзакцию, если все данные указаны верно
            balance_to_chosen = post_data.get('balance_to', None)
            balances_from_chosen = post_data.get('balances_from', None)
            sum_of_transaction = float(post_data['sum'][0])
            if balance_to_chosen is None or balances_from_chosen is None:  # дополнительная валидация
                context['error'] = 'Need to choose one balance to send money to'
            else:  # транзакция корректна, проверяем балансы на наличие достаточного кол-ва денег
                count_of_balances = len(balances_from_chosen)
                for pk in balances_from_chosen:
                    balance = Balance.objects.get(pk=pk)
                    if balance.sum < sum_of_transaction / count_of_balances:
                        context['error'] = 'Balance "' + balance.name + '" has not enough money'
                        break
                # везде хватает денег, тогда производим изменение балансов
                balances = []
                for pk in balances_from_chosen:
                    balance = Balance.objects.get(pk=pk)
                    balance.sum -= sum_of_transaction / count_of_balances
                    round(balance.sum, 3)
                    balance.save()
                    balances.append(balance)  # добавлем счета в список, для создания транзакции

                balance = Balance.objects.get(pk=balance_to_chosen[0])
                balance.sum += sum_of_transaction
                round(balance.sum, 3)
                balance.save()

                transaction = Transaction.objects.create(sum=sum_of_transaction, balance_to=balance)
                transaction.balances_from.set(balances)
                transaction.save()
                return redirect('base')

            if context.get('error', None) is not None:  # валидация не пройдена
                context['form'] = form
        else:
            context['form'] = form
    else:
        context['form'] = MakeTransaction()

    return render(request, 'main/transaction.html', context=context)


@login_required()
def balance_info(request, balance_pk):
    context = {'current_user': request.user.username}
    balance = get_object_or_404(Balance, pk=balance_pk)  # ??
    transactions_to = Transaction.objects.filter(balance_to__pk=balance_pk)  # зачисления
    transactions_from = Transaction.objects.filter(balances_from__pk=balance_pk)  # списание
    print(transactions_from)
    context['income'] = transactions_to
    context['expense'] = transactions_from
    return render(request, 'main/balance_info.html', context=context)


class TransactionList(ListView):
    model = Transaction
    login_url = 'accounts/login/'
    redirect_field_name = 'redirect_to'
    paginate_by = 10
    template_name = 'main/transaction_for_user.html'

    def get_queryset(self):
        filter_val = self.request.GET.get('filter', None)
        user = self.request.user.username
        transactions_to = Transaction.objects.filter(balance_to__user__username=user)  # только данные пользователя
        if filter_val is not None:  # если в филтр что-то передали
            transactions_to = transactions_to.filter(balance_to__user__username=filter_val)
        transactions_from = Transaction.objects.filter(balances_from__user__username=user).distinct()  #
        new_context = transactions_to.union(transactions_from)
        return new_context

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.request.GET.get('filter', "")
        context['current_user'] = self.request.user.username
        return context


class UserList(LoginRequiredMixin, ListView):
    model = User
    login_url = 'accounts/login/'
    redirect_field_name = 'redirect_to'
    paginate_by = 10
    template_name = 'main/users_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_user'] = self.request.user.username
        return context


# Блок аутентификации

def registration_view(request):
    context = {}
    if request.POST:
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_pass = form.cleaned_data.get('password1')
            participant = authenticate(username=username, password=raw_pass)
            login(request, participant)
            return redirect('base')
        else:
            context['registration_form'] = form
    else:  # GET
        form = RegistrationForm()
        context['registration_form'] = form
    return render(request, 'django_registration/registration_form.html', context)


def login_view(request):
    context = {}
    if request.POST:
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(username=cd['username'], password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('base')
                else:
                    return HttpResponse('Disabled account')
            else:
                return HttpResponse('Invalid login')
        else:
            context['login_form'] = form
    else:  # GET
        form = LoginForm()
        context['login_form'] = form
    return render(request, 'django_registration/login.html', context)

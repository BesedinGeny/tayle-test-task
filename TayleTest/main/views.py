from django.contrib.auth import login, authenticate
from django.http import HttpResponse
from django.shortcuts import render, redirect


# Create your views here.
from .forms import RegistrationForm, LoginForm


def base(request):
    return render(request, 'main/base.html', context={
        'current_user': request.user.username
    })


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

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from .forms import SignUpForm
from dailylearnings.models import Page
from learning.models import Profile


def home(request):
    return render(request, 'base/home.html', {'page': Page.HOME.value})


def template_page(request):
    return HttpResponse('Template HTTP FILE')


def login_page(request):
    form = AuthenticationForm()

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        print(username)
        print(password)
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist!')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username or Password is not correct.')

    context = {'page': Page.LOGIN.value, 'form': form}
    return render(request, 'base/login_register.html', context)


def logout_user(request):
    logout(request)
    return redirect('home')


def register_page(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            Profile.objects.create(
                user=user,
            )
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An error occurred during registration.')
    else:
        form = SignUpForm()
    context = {'page': Page.REGISTER.value, 'form': form}
    return render(request, 'base/login_register.html', context)

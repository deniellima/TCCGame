from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.urls import reverse
from firebase_admin import auth
import json

def home(request):
    return render(request, 'index.html')
<<<<<<< HEAD
=======

# Auth
>>>>>>> a07a37cc9bd7df2c802bae009129517e1ed65154

def register(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = auth.create_user(
                uid=name,
                email=email,
                password=password,
                email_verified=False,
            )
            auth.generate_email_verification_link(user.email)
            messages.success(request, f'Usuário criado com sucesso: {user.uid}')
            return redirect(reverse('login'))
        except Exception as e:
            messages.error(request, f'Erro ao criar usuário: {e}')
<<<<<<< HEAD
            return render(request, 'userRegister.html', {'error': 'Erro ao criar usuário. Tente novamente.'})
    
    return render(request, 'userRegister.html', {'error': None})
=======
            return render(request, 'register.html', {'error': 'Erro ao criar usuário. Tente novamente.'})
    
    return render(request, 'register.html', {'error': None})

>>>>>>> a07a37cc9bd7df2c802bae009129517e1ed65154

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        id_token = request.POST.get('idToken')

        if not id_token:
            messages.error(request, 'Token de autenticação não fornecido')
            return redirect(reverse('login'))

        try:
            decoded_token = auth.verify_id_token(id_token)
            uid = decoded_token['uid']
            firebase_user = auth.get_user(uid)

            if firebase_user and firebase_user.email == email: # user.email_verified
                user, created = User.objects.get_or_create(username=firebase_user.email, defaults={'email': firebase_user.email})

                auth_login(request, user)
                messages.success(request, 'Usuário logado com sucesso')
                return redirect(reverse('account'))
            else:
                messages.error(request, 'Email não encontrado ou não corresponde')

        except auth.AuthError as e:
            messages.error(request, f'Erro de autenticação: {e}')
        except Exception as e:
            messages.error(request, f'Erro ao fazer login: {e}')
    
    return redirect(reverse('login'))


def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']

        try:
            auth.generate_password_reset_link(email)
            messages.success(request, "Um e-mail de redefinição de senha foi enviado. Verifique sua caixa de entrada.")
            return redirect(reverse('login'))
        except Exception as e:
            messages.error(request, f'Erro ao enviar e-mail de redefinição de senha: {e}')
            return redirect(reverse('forgotPassword'))
    
<<<<<<< HEAD
    return render(request, 'userForgot.html')

def account(request):
    if request.user.is_authenticated:
        return render(request, 'userAccount.html')
=======
    return render(request, 'forgotPassword.html')

def account(request):
    if request.user.is_authenticated:
        return render(request, 'account.html')
>>>>>>> a07a37cc9bd7df2c802bae009129517e1ed65154
    else:
        return redirect(reverse('login'))

def logout(request):
    auth_logout(request)
    return redirect(reverse('login'))

# Games

def gameHangman(request):
<<<<<<< HEAD
    return render(request, 'gameHangman.html')

def gameMemory(request):
    return render(request, 'gameMemory.html')

def gameWordle(request):
    return render(request, 'gameWordle.html')

def gameLinguage(request):
    return render(request, 'gameLinguage.html')
=======
    return render(request, 'hangman.html')

def gameMemory(request):
    return render(request, 'memory.html')

def gameWordle(request):
    return render(request, 'wordle.html')
>>>>>>> a07a37cc9bd7df2c802bae009129517e1ed65154

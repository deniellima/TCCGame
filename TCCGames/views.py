from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.urls import reverse
from firebase_admin import auth

def home(request):
    return render(request, 'index.html')

def register(request):
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            email = request.POST.get('email')
            password = request.POST.get('password')

            if User.objects.filter(email=email).exists():
                messages.error(request, 'O e-mail já está registrado.')
                return render(request, 'userRegister.html', {'error': 'O e-mail já está registrado.'})

            user_django = User.objects.create_user(
                username=name,
                email=email, 
                password=password
            )

            user = auth.create_user(
                display_name=name,
                email=email,
                password=password,
                email_verified=False,
            )
            auth.generate_email_verification_link(user.email)

            messages.success(request, f'Usuário criado com sucesso: {user.display_name}.  Verifique seu email: {user_django.email} para completar a verificação.')
            return redirect(reverse('login'))
        except Exception as e:
            messages.error(request, f'Erro ao criar usuário: {e}')
            return render(request, 'userRegister.html', {'error': 'Erro ao criar usuário. Tente novamente.'})
    
    return render(request, 'userRegister.html', {'error': None})

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        print(f"Email: {email}")
        print(f"Password: {password}")

        try:
            user_django = authenticate(request, email=email, password=password)
            print(f"User Django: {user_django}")

            firebase_user = auth.get_user_by_email(email)
            print(f"Firebase User: {firebase_user}")

            if user_django is not None and firebase_user is not None:
                auth_login(request, user_django)
                messages.success(request, 'Login realizado com sucesso!')
                return redirect('account')
            else:
                print("User Django ou Firebase User é None")
                messages.error(request, 'Credenciais inválidas ou usuário não registrado.')
                return redirect('register')
        except Exception as e:
            messages.error(request, f'Erro ao fazer login: {e}')
            return render(request, 'userLogin.html', {'erro': 'Credenciais inválidas. Tente novamente.'})
        
    return render(request, 'userLogin.html', {'error': None})

def account(request):
    if request.user.is_authenticated:
        return render(request, 'userAccount.html')
    else:
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
    
    return render(request, 'userForgot.html')

def logout(request):
    auth_logout(request)
    return redirect(reverse('login'))

# Games

def gameHangman(request):
    return render(request, 'gameHangman.html')

def gameMemory(request):
    return render(request, 'gameMemory.html')

def gameWordle(request):
    return render(request, 'gameWordle.html')

def gameLinguage(request):
    return render(request, 'gameLinguage.html')

def privacy(request):
    return render(request, 'privacy.html')
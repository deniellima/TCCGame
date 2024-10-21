from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from app.config import firebase, db
from django.http import JsonResponse
from .decorators import login_required

auth = firebase.auth()

def home(request):
    return render(request, 'index.html')

# Users

def register(request):
    if 'uid' in request.session:
        return redirect('account')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        name = request.POST.get('name')
        password = request.POST.get('password')
        verifyPassword = request.POST.get('verify-password')

        if password != verifyPassword:
            messages.error(request, 'As senhas não coincidem!')
            return redirect('register')

        try:
            user = auth.create_user_with_email_and_password(email, password)
            messages.success(request, f'Usuário {name} registrado com sucesso!')
            return redirect('login')
        except Exception as e:
            messages.error(request, f'Erro ao registrar: {str(e)}')
            return redirect('register')

    return render(request, 'userRegister.html')

def login(request):
    if 'uid' in request.session:
        return redirect('account')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = auth.sign_in_with_email_and_password(email, password)
            session_id = user['idToken']
            request.session['uid'] = str(session_id)
            messages.success(request, 'Login realizado com sucesso!')
            return redirect('account')
        except Exception as e:
            messages.error(request, f"Erro ao fazer login: {str(e)}")
            return render(request, 'userLogin.html')
    return render(request, 'userLogin.html')

@login_required
def account(request):
    return render(request, 'userAccount.html')


def forgotPassword(request):
    if 'uid' in request.session:
        return redirect('account')

    if request.method == 'POST':
        email = request.POST.get('email')

        try:
            auth.generate_password_reset_link(email)
            messages.success(request, "Um e-mail de redefinição de senha foi enviado. Verifique sua caixa de entrada.")
            return redirect(reverse('login'))
        except Exception as e:
            messages.error(request, f'Erro ao enviar e-mail de redefinição de senha: {e}')
            return redirect(reverse('forgotPassword'))
    
    return render(request, 'userForgot.html')

@login_required
def logout(request):
    try:
        del request.session['uid']
    except KeyError:
        pass
    messages.success(request, 'Logout realizado com sucesso!')
    return redirect('login')


def privacy(request):
    return render(request, 'privacy.html')

# Score logic

def update_score(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido.'}, status=405)

    usuario_id = request.user.id
    novo_score = request.POST.get('score')

    if novo_score is not None:
        try:
            novo_score = int(novo_score)

            user_data = db.child("usuarios").child(usuario_id).get().val()
            score_user = user_data.get('score', 0)

            score = score_user + novo_score
            db.child("usuarios").child(usuario_id).update({"score": score})

            return JsonResponse({'message': 'Score atualizado com sucesso!', 'score': score})

        except ValueError:
            return JsonResponse({'error': 'Score deve ser um número inteiro.'}, status=400)

    return JsonResponse({'error': 'Score não fornecido.'}, status=400)


def list_users_by_score(request):
    usuarios = db.child("usuarios").order_by_child("score").get()

    lista_usuarios = [(usuario.key(), usuario.val()) for usuario in usuarios.each()]

    lista_usuarios = sorted(lista_usuarios, key=lambda x: x['score'], reverse=True)

    return render(request, 'lista_usuarios.html', {'usuarios': lista_usuarios})

def recover_user_data(request):
    usuario_id = request.user.id
    user_data = db.child("usuarios").child(usuario_id).get().val()
    score = user_data.get('score', 0)
    level = user_data.get('level', 0)

    return render(request)

@login_required
def gameHangman(request):
    total_points = 0 

    if request.method == 'POST':
        
        response = update_score(request)
        total_points = response.get('score', 0)

    return render(request, 'gameHangman.html', {'total_points': total_points})

# Games

@login_required
def gameMemory(request):
    total_points = 0 

    if request.method == 'POST':
        
        response = update_score(request)
        total_points = response.get('score', 0)

    return render(request, 'gameMemory.html', {'total_points': total_points})

@login_required
def gameWordle(request):
    total_points = 0 

    if request.method == 'POST':
        
        response = update_score(request)
        total_points = response.get('score', 0)

    return render(request, 'gameWordle.html', {'total_points': total_points})

@login_required
def gameLinguage(request):
    total_points = 0 

    if request.method == 'POST':
        
        response = update_score(request)
        total_points = response.get('score', 0)

    return render(request, 'gameLinguage.html', {'total_points': total_points})
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from app.config import firebase, db
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
# from firebase_admin import auth as admin_auth
# from .decorators import login_required
# from django.views.decorators.cache import cache_page
import json

auth = firebase.auth()

def home(request):
    return render(request, 'index.html')


# -------------------- Users --------------------

@csrf_exempt
def register(request):
    '''
    Register a new user in the system using email and password for authentication in firebase.
    '''
    if 'uid' in request.session:
        return redirect('home')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        name = request.POST.get('name')
        password = request.POST.get('password')
        verifyPassword = request.POST.get('confirm-password')

        if password != verifyPassword:
            messages.error(request, 'As senhas não coincidem!')
            return redirect('register')

        try:
            user = auth.create_user_with_email_and_password(email, password)
            db.child("users").child(user['localId']).set({
                "name": name,
                "points": 0,
                "level": 1
            })

            messages.success(request, f'Usuário {name} registrado com sucesso!')
            return redirect('login')
        except Exception as e:
            error_message = "Erro ao registrar. Por favor, tente novamente."
            error_str = str(e)

            if "EMAIL_EXISTS" in error_str:
                error_message = "O e-mail já está registrado."
            elif "WEAK_PASSWORD" in error_str:
                error_message = "A senha deve ter pelo menos 6 caracteres."
            elif "TOO_MANY_ATTEMPTS_TRY_LATER" in error_str:
                error_message = "Muitas tentativas de registro. Tente novamente mais tarde."
            messages.error(request, error_message)
            return redirect('register')

    return render(request, 'userRegister.html')

@csrf_exempt
def login(request):
    '''
    Realize the login of a user in the system using email and password for authentication in firebase, saving the authentication token in the user's session.
    '''
    if 'uid' in request.session:
        return redirect('account')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not email or not password:
            messages.error(request, 'Email e senha são obrigatórios.')
            return redirect('login')

        try:
            user = auth.sign_in_with_email_and_password(email, password)
            session_id = user['localId']
            request.session['uid'] = session_id
            print(f"ID do usuário: {session_id}")

            messages.success(request, 'Login realizado com sucesso!')
            return redirect('home')
        except Exception as e:
            error_message = f"Erro ao fazer login. Por favor, tente novamente."
            error_str = str(e)

            if "EMAIL_NOT_FOUND" in error_str:
                error_message = "E-mail não registrado. Verifique os dados ou registre-se."
            elif "INVALID_LOGIN_CREDENTIALS" in error_str:
                error_message = "As suas credenciais estão incorretas, tenta novamente."
            elif "USER_DISABLED" in error_str:
                error_message = "Esta conta foi desativada. Entre em contato com o suporte."
            elif "TOO_MANY_ATTEMPTS_TRY_LATER" in error_str:
                error_message = "Muitas tentativas de login. Tente novamente mais tarde."
            messages.error(request, error_message)
            return redirect('login')
    return render(request, 'userLogin.html')


def account(request):
    '''
    Render the user account page.
    '''
    if 'uid' not in request.session:
        return redirect('login')
    return render(request, 'userAccount.html')

@csrf_exempt
def forgotPassword(request):
    '''
    Send a password reset email to the user's email.
    '''
    if 'uid' in request.session:
        return redirect('account')

    if request.method == 'POST':
        email = request.POST.get('email')

        if not email:
            messages.error(request, 'Por favor, forneça um email válido.')
            return redirect(reverse('forgotPassword'))
        try:
            auth.send_password_reset_email(email)
            messages.success(request, "Um e-mail de redefinição de senha foi enviado. Verifique sua caixa de entrada.")
            return redirect(reverse('login'))
        except Exception as e:
            messages.error(request, f'Erro ao enviar e-mail de redefinição de senha: {e}')
            return redirect(reverse('forgotPassword'))
    
    return render(request, 'userForgot.html')


def logout(request):
    '''
    Release the user's authentication token from the session.
    '''
    if 'uid' not in request.session:
        return redirect('home')
    
    try:
        del request.session['uid']
    except KeyError:
        pass
    messages.success(request, 'Logout realizado com sucesso!')
    print("Logout realizado com sucesso!")
    return redirect('login')


# -------------------- Score logic --------------------

@csrf_exempt
def update_score(request):
    '''
    Update the user's score in the Firebase database.
    '''

    if request.method == 'POST':
        try:
            user_id = request.session.get('uid', None)
            if not user_id:
                return JsonResponse({"error": "Usuário não autenticado"}, status=401)
            print(user_id)

            data = json.loads(request.body)
            points_earned = int(data.get('points_earned', 0))

            user_data = db.child("users").child(user_id).get().val()
            if not user_data:
                user_data = {"points": 0, "level": 0}

            points = user_data.get('points', 0) + points_earned
            level = points // 100

            db.child("users").child(user_id).update({
                "points": points,
                "level": level
            })

            return JsonResponse(
                {"points": points, "level": level}
            )

        except json.JSONDecodeError:
            return JsonResponse({"error": "Dados inválidos no corpo da requisição"}, status=400)
        except Exception as e:
            return JsonResponse({"error": f"Erro ao atualizar pontuação: {str(e)}"}, status=500)
    else:
        return JsonResponse({"error": "Método não permitido"}, status=405)
    

@csrf_exempt
def position_users(request):
    '''
    Recupera a posição do jogador atual e as 3 primeiras posições globais com base nos pontos.
    '''
    user_id = request.session.get('uid', None)
    
    try:
        all_users = db.child("users").get().val()
        
        if not all_users:
            return JsonResponse({"error": "Nenhum dado de usuários encontrado."}, status=404)

        sorted_users = sorted(all_users.items(), key=lambda x: x[1].get('points', 0), reverse=True)

        user_position = None
        for index, (uid, data) in enumerate(sorted_users, start=1):
            if uid == user_id:
                user_position = {
                    "position": index,
                    "user_id": uid,
                    "name": data.get("name", "Anônimo"),
                    "points": data.get("points", 0),
                    "level": data.get("level", 0)
                }
                break

        top_3 = [
            {
                "position": index,
                "user_id": uid,
                "name": data.get("name", "Anônimo"),
                "points": data.get("points", 0),
                "level": data.get("level", 0)
            }
            for index, (uid, data) in enumerate(sorted_users[:3], start=1)
        ]

        return JsonResponse({
            "user_position": user_position,
            "top_3": top_3
        })
    except Exception as e:
        return JsonResponse({"error": f"Erro ao recuperar dados: {str(e)}"}, status=500)


@csrf_exempt
def user_data(request):
    """
    Recover the user's data for listing on the home page.
    """
    user_id = request.session.get('uid', None)
    if not user_id:
        return JsonResponse({"error": "Usuário não autenticado"}, status=401)
    print(f"uid para request home: {user_id}")
    try:
        user_data = db.child("users").child(user_id).get().val()
        if not user_data:
            user_data = {"points": 0, "level": 0}

        return JsonResponse({
            "level": user_data["level"],
            "points": user_data["points"],
            "name": user_data["name"],
        })
    except Exception as e:
        print(f"Erro ao recuperar dados: {str(e)}") 
        return JsonResponse({"error": f"Erro ao recuperar dados da página inicial: {str(e)}"}, status=500)
    
@csrf_exempt
def update_name(request):
    """
    Updates the user's name in the Firebase database.
    """
    if request.method == 'POST':
        try:
            user_id = request.session.get('uid', None)
            if not user_id:
                return JsonResponse({"error": "Usuário não autenticado"}, status=401)

            data = json.loads(request.body)
            new_name = data.get('name')

            if not new_name:
                return JsonResponse({"error": "Escolha um novo nome para aplicar"}, status=400)

            db.child("users").child(user_id).update({
                "name": new_name
            })

            return JsonResponse({"message": "Nome atualizado com sucesso!"})
        except Exception as e:
            return JsonResponse({"error": f"Erro ao atualizar nome: {str(e)}"}, status=500)
    else:
        return JsonResponse({"error": "Método não permitido"}, status=405)



# -------------------- Games --------------------


def gameHangman(request):
    '''
    Render the hangman game page.
    '''
    if 'uid' not in request.session:
        messages.error(request, f'Você precisa estar logado para executar essa ação')
        return redirect('home')
    
    return render(request, 'gameHangman.html')


def gameMemory(request):
    '''
    Render the memory game page.
    '''
    if 'uid' not in request.session:
        messages.error(request, f'Você precisa estar logado para executar essa ação')
        return redirect('home')
    
    return render(request, 'gameMemory.html')


def gameWordle(request):
    '''
    Render the wordle game page.
    '''
    if 'uid' not in request.session:
        messages.error(request, f'Você precisa estar logado para executar essa ação')
        return redirect('home')
    
    return render(request, 'gameWordle.html')


def gameLinguage(request):
    '''
    Render the language game page.
    '''
    if 'uid' not in request.session:
        messages.error(request, f'Você precisa estar logado para executar essa ação')
        return redirect('home')
    
    return render(request, 'gameLinguage.html')

def privacy(request):
    '''
    Render the privacy policy page.
    '''
    return render(request, 'privacy.html')
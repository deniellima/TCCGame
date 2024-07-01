from firebase_admin import auth
from flask import Flask, request, render_template, redirect, url_for, session, flash
import config
import os

config.connection

app = Flask(__name__, template_folder='../', static_folder='../')
app.config.from_object('config')

@app.route('/')
def home():
    return render_template("home/index.html")


@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        try:
            user = auth.create_user(
                uid=name,
                email=email,
                password=password,
                email_verified=False,
            )

            auth.generate_email_verification_link(user.email)

            flash('Usuário criado com sucesso:', user.uid)
            return redirect(url_for('login'))
        except Exception as e:
            flash('Erro ao criar usuário:', e)
            return render_template("register/register.html", error='Erro ao criar usuário. Tente novamente.')
        
    return render_template("register/register.html", error=None)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            user = auth.get_user_by_email(email)
            if user and user.email_verified:
                auth_user = auth.verify_password(password, user)
                if auth_user:
                    session['user'] = {
                        'uid': auth_user.uid,
                        'email': auth_user.email,
                        'name': auth_user.display_name
                    }
                    flash('Usuário logado com sucesso:', user.uid)
                    return redirect(url_for('account'))
                else:
                    return "Senha incorreta"
            else:
                return "E-mail não verificado"
        except Exception as e:
            flash('Erro ao fazer login:', e)
            return render_template("login.html", error='Erro ao fazer login. Verifique suas credenciais.')
        
    return render_template('login/login.html', error=None)


@app.route('/forgotPassword', methods=['GET', 'POST'])
def forgotPassword():
    if request.method == 'POST':
        email = request.form['email']
        try:
            auth.generate_password_reset_link(email)
            flash("Um e-mail de redefinição de senha foi enviado. Verifique sua caixa de entrada.")
            return redirect(url_for('login'))
        except Exception as e:
            print('Erro ao enviar e-mail de redefinição de senha:', e)
            flash("Erro ao enviar e-mail de redefinição de senha. Tente novamente.")
            return redirect(url_for('forgotPassword'))

    return render_template("forgotpassword/forgotPassword.html")


@app.route('/account')
def account():
    if 'user' in session:
        return render_template("account/account.html")
    else:
        return redirect(url_for('login'))


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)), debug=True)
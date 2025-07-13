from flask import Flask, render_template, request, redirect, url_for, session, make_response
import requests
import os

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = os.getenv("SECRET_KEY", "frontendsecret")

BACKEND_URL = os.getenv("BACKEND_URL", "http://auth_service:8001/api")

def get_auth_cookies():
    cookies = {}
    if 'session' in request.cookies:
        cookies['session'] = request.cookies.get('session')
    return cookies

@app.route('/', methods=['GET'])
def home():
    if 'user_id' in session:
        return render_template('home.html')
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone = request.form['phone']
        resp = requests.post(f"{BACKEND_URL}/login", json={'phone': phone}, cookies=get_auth_cookies())
        if resp.ok:
            session['login_phone'] = phone
            return render_template('code.html', phone=phone, action='login-verify')
        return render_template('login.html', error="Ошибка отправки кода")
    return render_template('login.html')

@app.route('/login-verify', methods=['POST'])
def login_verify():
    code = request.form['code']
    phone = session.get('login_phone')
    resp = requests.post(f"{BACKEND_URL}/login-verify", json={'code': code}, cookies=get_auth_cookies())
    if resp.ok and resp.json().get('status') == 'ok':
        session['user_id'] = True
        return redirect(url_for('home'))
    return render_template('code.html', phone=phone, action='login-verify', error="Неверный код")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        phone = request.form['phone']
        resp = requests.post(f"{BACKEND_URL}/register", json={'phone': phone}, cookies=get_auth_cookies())
        if resp.ok:
            session['reg_phone'] = phone
            return render_template('code.html', phone=phone, action='verify')
        return render_template('register.html', error="Ошибка отправки кода")
    return render_template('register.html')

@app.route('/verify', methods=['POST'])
def verify():
    code = request.form['code']
    phone = session.get('reg_phone')
    name = request.form.get('name', '')
    surname = request.form.get('surname', '')
    resp = requests.post(
        f"{BACKEND_URL}/verify",
        json={'code': code, 'name': name, 'surname': surname},
        cookies=get_auth_cookies()
    )
    if resp.ok and resp.json().get('status') == 'ok':
        session['user_id'] = True
        return redirect(url_for('home'))
    return render_template('code.html', phone=phone, action='verify', error="Неверный код")

@app.route('/profile')
def profile():
    resp = requests.get(f"{BACKEND_URL}/profile", cookies=get_auth_cookies())
    if resp.status_code == 200:
        return render_template('profile.html', **resp.json())
    return redirect(url_for('login'))

@app.route('/profile-edit', methods=['GET', 'POST'])
def profile_edit():
    if request.method == 'POST':
        data = {
            'name': request.form['name'],
            'surname': request.form['surname'],
            'avatar': request.form['avatar']  # base64 string
        }
        resp = requests.post(f"{BACKEND_URL}/profile", json=data, cookies=get_auth_cookies())
        if resp.ok:
            return redirect(url_for('profile'))
        return render_template('profile_edit.html', error="Ошибка сохранения")
    resp = requests.get(f"{BACKEND_URL}/profile", cookies=get_auth_cookies())
    if resp.status_code == 200:
        return render_template('profile_edit.html', **resp.json())
    return redirect(url_for('login'))

@app.route('/delete', methods=['POST'])
def delete():
    requests.post(f"{BACKEND_URL}/delete", cookies=get_auth_cookies())
    session.clear()
    return redirect(url_for('login'))

@app.route('/logout', methods=['POST'])
def logout():
    requests.post(f"{BACKEND_URL}/logout", cookies=get_auth_cookies())
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)

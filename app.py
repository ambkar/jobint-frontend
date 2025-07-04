from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import requests
import jwt

SECRET_KEY = '732e4de0c7203b17f73ca043a7135da261d3bff7c501a1b1451d6e5f412e2396'
AUTH_API = "https://jobint.ru/api/v1/auth"

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    token = None
    # Получаем токен из заголовка Authorization
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
    # Если токен хранится в cookie:
    # token = request.cookies.get('access_token')

    user = None
    if token:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            user = payload.get('user_id')  # или другое поле
        except jwt.ExpiredSignatureError:
            pass
        except jwt.InvalidTokenError:
            pass

    if user:
        return render_template('index_auth.html', user=user)
    else:
        return render_template('index.html')

@app.route("/login", methods=["GET"])
def login_page():
    return render_template("login.html")

@app.route("/register", methods=["GET"])
def register_page():
    return render_template("register.html")

@app.route("/auth/login", methods=["POST"])
def login_api():
    data = request.json
    resp = requests.post(f"{AUTH_API}/login", json=data, verify=False)
    return (resp.text, resp.status_code, resp.headers.items())

@app.route("/auth/register", methods=["POST"])
def register_api():
    # Получаем все поля формы как словарь
    data = request.form.to_dict()
    files = {}
    if 'avatar' in request.files and request.files['avatar'].filename:
        avatar = request.files['avatar']
        files['avatar'] = (avatar.filename, avatar, avatar.mimetype)
    resp = requests.post(f"{AUTH_API}/register", data=data, files=files)

    # Пересылаем запрос на микросервис авторизации
    resp = requests.post(
        f"{AUTH_API}/register",
        data=data,
        files=files if files else None,
        verify=False
    )
    # Возвращаем ответ клиента (статус, тело, заголовки)
    return (resp.text, resp.status_code, resp.headers.items())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

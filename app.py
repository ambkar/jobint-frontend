from flask import Flask, render_template, request, make_response, redirect, url_for
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
import requests

SECRET_KEY = '732e4de0c7203b17f73ca043a7135da261d3bff7c501a1b1451d6e5f412e2396'
AUTH_API = "https://jobint.ru/api/v1/auth"

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    token = request.cookies.get('access_token')
    user = None
    if token:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            user = payload.get('user')  # <-- исправлено тут!
        except ExpiredSignatureError:
            pass
        except InvalidTokenError:
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
    # Проксируем запрос на сервис авторизации
    resp = requests.post(f"{AUTH_API}/login", json=data, verify=False)
    response = make_response(resp.text, resp.status_code)
    try:
        # Пытаемся получить токен из ответа
        token = resp.json().get('token')
        if token:
            # Устанавливаем токен в cookie (httpOnly и secure для безопасности)
            response.set_cookie(
                'access_token',
                token,
                httponly=True,
                secure=True,  # Только если у вас HTTPS! Для локальной разработки можно убрать
                samesite='Lax',
                domain='.jobint.ru'
            )
    except Exception:
        pass
    return response

@app.route("/auth/register", methods=["POST"])
def register_api():
    # Получаем все поля формы как словарь
    data = request.form.to_dict()
    files = {}
    if 'avatar' in request.files and request.files['avatar'].filename:
        avatar = request.files['avatar']
        files['avatar'] = (avatar.filename, avatar, avatar.mimetype)
    # Проксируем запрос на сервис авторизации
    resp = requests.post(
        f"{AUTH_API}/register",
        data=data,
        files=files if files else None,
        verify=False
    )
    return (resp.text, resp.status_code, resp.headers.items())

@app.route("/logout")
def logout():
    response = redirect(url_for("index"))
    response.delete_cookie("access_token", domain=".jobint.ru")  # domain укажите тот же, что при установке!
    return response

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

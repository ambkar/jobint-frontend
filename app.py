from flask import Flask, render_template, request, redirect, url_for, jsonify
import requests

AUTH_API = "https://jobint.ru/api/v1/auth"

app = Flask(__name__)

@app.route("/")
def home():
    return "Welcome to the homepage!"

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

from flask import Flask, render_template, request, redirect, url_for, jsonify
import requests

AUTH_API = "https://jobint.ru/api/v1/auth"

app = Flask(__name__)

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
    data = request.form.to_dict()
    files = {}

    # Если был аватар — добавляем его к запросу
    if 'avatar' in request.files and request.files['avatar'].filename:
        avatar = request.files['avatar']
        # requests ожидает кортеж: (filename, fileobj, mimetype)
        files['avatar'] = (avatar.filename, avatar.stream, avatar.mimetype)

    resp = requests.post(f"{AUTH_API}/register", data=data, files=files, verify=False)
    return (resp.text, resp.status_code, resp.headers.items())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

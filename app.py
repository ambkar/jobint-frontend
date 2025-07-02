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
    # Аватар (если был) — отдельной строкой
    files = {}
    if 'avatar' in request.files and request.files['avatar'].filename:
        files['avatar'] = request.files['avatar'].stream
    resp = requests.post(f"{AUTH_API}/register", data=data, files=files, verify=False)
    return (resp.text, resp.status_code, resp.headers.items())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)

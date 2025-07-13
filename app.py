from flask import Flask, render_template, request, make_response, redirect, url_for, flash
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
import requests

SECRET_KEY = '732e4de0c7203b17f73ca043a7135da261d3bff7c501a1b1451d6e5f412e2396'
AUTH_API = "https://jobint.ru/api/v1/auth"

app = Flask(__name__)
app.secret_key = SECRET_KEY  # Обязательно задайте уникальный секрет!

@app.route("/", methods=["GET"])
def index():
    token = request.cookies.get('access_token')
    if not token:
        return render_template('index.html')
    headers = {"Authorization": f"Bearer {token}"}
    try:
        resp = requests.get(f"{AUTH_API}/me", headers=headers, verify=False)
        if resp.status_code == 200:
            user = resp.json().get("user")
            return render_template('index_auth.html', user=user)
        else:
            return render_template('index.html')
    except Exception:
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
    response = make_response(resp.text, resp.status_code)
    try:
        token = resp.json().get('token')
        if token:
            response.set_cookie(
                'access_token',
                token,
                httponly=True,
                secure=True,
                samesite='Lax',
                domain='.jobint.ru'
            )
    except Exception:
        pass
    return response

@app.route("/auth/register", methods=["POST"])
def register_api():
    data = request.form.to_dict()
    files = {}
    if 'avatar' in request.files and request.files['avatar'].filename:
        avatar = request.files['avatar']
        files['avatar'] = (avatar.filename, avatar, avatar.mimetype)
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
    response.delete_cookie(
        "access_token",
        domain=".jobint.ru",
        path="/"
    )
    return response

@app.route("/profile", methods=["GET", "POST"])
def profile():
    token = request.cookies.get('access_token')
    if not token:
        return redirect(url_for("login_page"))
    headers = {"Authorization": f"Bearer {token}"}

    if request.method == "POST":
        data = {
            "name": request.form.get("name"),
            "surname": request.form.get("surname"),
            "patronymic": request.form.get("patronymic"),
            "phone": request.form.get("phone"),
            "email": request.form.get("email"),
        }
        files = {}
        password = request.form.get("password")
        if password:
            data["password"] = password
        avatar_file = request.files.get("avatar")
        if avatar_file and avatar_file.filename:
            files["avatar"] = (avatar_file.filename, avatar_file.stream, avatar_file.mimetype)
        try:
            resp = requests.put(
                f"{AUTH_API}/profile",
                data=data,
                files=files if files else None,
                headers=headers,
                timeout=10,
                verify=False
            )
            if resp.status_code == 200:
                flash("Профиль обновлён", "success")
            else:
                try:
                    error_json = resp.json()
                    error_msg = error_json.get('error', 'Неизвестная ошибка')
                except Exception:
                    error_msg = f"HTTP {resp.status_code}: {resp.text}"
                flash(f"Ошибка обновления: {error_msg}", "error")
        except Exception as e:
            flash(f"Ошибка соединения с сервисом авторизации: {e}", "error")
        # После изменения профиля сразу получаем актуальные данные
        resp = requests.get(f"{AUTH_API}/me", headers=headers, verify=False)
        user_data = resp.json().get("user") if resp.status_code == 200 else None
        return render_template("profile.html", user=user_data)

    # GET-запрос — всегда получаем актуальные данные профиля через /me
    resp = requests.get(f"{AUTH_API}/me", headers=headers, verify=False)
    user_data = resp.json().get("user") if resp.status_code == 200 else None
    return render_template("profile.html", user=user_data)

@app.route("/profile/delete", methods=["POST"])
def delete_profile():
    token = request.cookies.get('access_token')
    if not token:
        return redirect(url_for("login_page"))
    headers = {"Authorization": f"Bearer {token}"}
    try:
        resp = requests.delete(f"{AUTH_API}/profile", headers=headers, verify=False)
        response = redirect(url_for("index"))
        response.delete_cookie("access_token", domain=".jobint.ru", path="/")
        if resp.status_code == 200:
            flash("Профиль удалён", "success")
        else:
            try:
                error_json = resp.json()
                error_msg = error_json.get('error', 'Неизвестная ошибка')
            except Exception:
                error_msg = f"HTTP {resp.status_code}: {resp.text}"
            flash(f"Ошибка удаления: {error_msg}", "error")
        return response
    except Exception as e:
        flash(f"Ошибка соединения с сервисом авторизации: {e}", "error")
        return redirect(url_for("profile"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

from flask import Flask, render_template, session, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from db_factory import DataBase
import mysql.connector
from queries import AUTH_USER, LOAD_USER, LOAD_ROLES, ADD_USER, GET_USERS, VIEW_USER, EDIT_USER, DELETE_USER
from utils import extract_form, edit_user_validation, create_user_validation, error_message, check_password

app = Flask(__name__)
application = app
app.config.from_pyfile('config.py')
db = DataBase(app)

class User(UserMixin):
    def __init__(self, id, login):
        self.id = id
        self.login = login

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Для доступа к этой странице необходимо пройти процедуру аутентификации.'
login_manager.login_message_category = 'warning'

@app.route('/')
def index():
    with db.connection.cursor(named_tuple = True) as cursor:
        cursor.execute(GET_USERS)
        print(cursor.statement)
        db_users = cursor.fetchall()
    return render_template('index.html', users = db_users)

#LOGIN
def authenticate_user(login, password):
    with db.connection.cursor(named_tuple = True) as cursor:
        cursor.execute(AUTH_USER, (login, password))
        print(cursor.statement)
        db_user = cursor.fetchone()
    if db_user:
        user = User(db_user.id, db_user.login)
        return user
    return None

def load_roles():
    with db.connection.cursor(named_tuple = True) as cursor:
        cursor.execute(LOAD_ROLES)
        db_roles = cursor.fetchall()
    return db_roles


@login_manager.user_loader
def load_user(user_id):
    cursor = db.connection.cursor(named_tuple = True)
    cursor.execute(LOAD_USER, (user_id,))
    db_user = cursor.fetchone()
    cursor.close()
    if db_user:
        user = User(user_id, db_user.login)
        return user
    return None


@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == "POST":
        user_login = request.form["loginInput"]
        user_password = request.form["passwordInput"]
        remember_me = request.form.get('remember_me') == 'on'

        auth_user = authenticate_user(user_login, user_password)
        if auth_user:
            login_user(auth_user, remember=remember_me)
            flash("Вы успешно авторизованы", "success")
            return redirect(request.args.get('next')or url_for("index"))
            
        flash("Введены неверные логин и/или пароль", "danger")
        redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for("index"))

#USERS

@app.route("/users/<int:user_id>")
def view_user(user_id):
    with db.connection.cursor(named_tuple = True) as cursor:
        cursor.execute(VIEW_USER, (user_id,))
        db_user = cursor.fetchone()
    if not db_user:
        flash("Пользователь не найден", "danger")
        return redirect(url_for("users"))
    return render_template('users/view.html', user=db_user)

def add_user(params):
    with db.connection.cursor(named_tuple = True) as cursor:
        cursor.execute(ADD_USER, params)
        db.connection.commit()
    return True

#Создание нового пользователя
@app.route('/users/new', methods=['GET', 'POST'])
@login_required
def new_user():
    if request.method == 'GET':
        return render_template('users/new.html', roles = load_roles(), user={}, errors={})
    if request.method == 'POST':
        formdata = extract_form()
        errors = create_user_validation(formdata)
        if errors["isvalidate"] == 0:
            flash("Проверьте правильность введённых данных", "danger")
            return render_template("users/new.html", roles = load_roles(), user=formdata, errors=errors)
        result = add_user(formdata)
        if not result:
            flash("При сохранении возникла ошибка", "danger")
            return render_template("users/new.html", roles = load_roles(), user=formdata, errors=errors)
        flash("Пользователь успешно добавлен", "success")
        return redirect(url_for("index"))

# Редактирование пользователя
@app.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if request.method == 'GET':
        errors = {}
        with db.connection.cursor(named_tuple = True) as cursor:
            cursor.execute(VIEW_USER, (user_id,))
            user = cursor.fetchone()
            if not user:
                flash("Пользователь не найден", "warning")
                return redirect(url_for("users"))
        return render_template("users/edit.html", user=user, roles=load_roles(), errors=errors)
    if request.method == 'POST':
        formdata = extract_form()
        errors = edit_user_validation(formdata)
        formdata["id"] = user_id
        if errors["isvalidate"] == 0:
            flash("Проверьте правильность введённых данных", "danger")
            return render_template('users/edit.html', user=formdata, roles=load_roles(), errors=errors)
        try:
            with db.connection.cursor(named_tuple = True) as cursor:
                cursor.execute(EDIT_USER, formdata)
                db.connection.commit()
                flash("Пользователь успешно обновлен", "success")
        except mysql.connector.errors.DatabaseError:
            flash("При редактировании пользователя возникла ошибка", "danger")
            db.connection.rollback()
            return render_template('users/edit.html', user=formdata, roles=load_roles(), errors=errors)
        return redirect(url_for("index"))

# Удаление пользователя
@app.route("/users/<int:user_id>/delete", methods=['POST'])
@login_required
def delete_user(user_id):
    try:
        with db.connection.cursor(named_tuple = True) as cursor:
            cursor.execute(DELETE_USER, (user_id,))
            db.connection.commit()
            flash("Пользователь успешно удален", "success")
    except mysql.connector.errors.DatabaseError:
        flash("При удалении произошла ошибка", "danger")
        db.connection.rollback()
    return redirect(url_for("index"))


@app.route("/users/change_password", methods=['GET', 'POST'])
@login_required
def change_password():
    user_id = current_user.id
    PERMITTED_PASSWORD = '''abcdefghijklmnopqrstuvwxyzабвгдеёжзийклмнопрстуфхцчшщъыьэюя1234567890~!?@#$%^&*_-+()[]{}></\|"'.,:;'''
    errors = {
        "old": None,
        "check": None,
        "password": None, 
        "ok": 1,
    }
    fields = {
        "old": "",
        "new": "",
        "check": "",
    }
    if request.method == "POST":
        old_passwd = request.form.get("floatingOldPassword")
        new_passwd = request.form.get("floatingNewPassword")
        check_new_passwd = request.form.get("floatingCheckPassword")
        fields["old"] = old_passwd
        fields["new"] = new_passwd
        fields["check"] = check_new_passwd
        query = "SELECT * FROM users WHERE id = %s AND password_hash = SHA2(%s, 256);"
        with db.connection.cursor(named_tuple = True) as cursor:
            cursor.execute(query, (user_id, old_passwd))
            print(cursor.statement)
            db_user = cursor.fetchone()
            if db_user is None:
                errors["old"] = error_message["INCORRECT_PASSWORD"]
                errors["ok"] = 0
            validate_password = check_password({"password": new_passwd}, PERMITTED_PASSWORD)
            if not validate_password.get("password") is None:
                errors["password"] = validate_password["password"]
                errors["check"] = validate_password["password"]
                errors["ok"] = 0
            if new_passwd != check_new_passwd:
                errors["check"] = error_message["WRONG_CONFIRMATION_PASSWORD"]
                errors["ok"] = 0
        if errors.get("ok") == 0:
            flash("Проверьте введённые данные", "danger")
            return render_template('change_password.html', errors=errors, fields=fields)
    
        update_query = "UPDATE users SET password_hash = SHA2(%s, 256) WHERE id = %s;"
        try:
            with db.connection.cursor(named_tuple = True) as cursor:
                cursor.execute(update_query, (new_passwd, user_id))
                db.connection.commit()
                flash("Пароль успешно обновлен", "success")
                return redirect(url_for("index"))
        except mysql.connector.errors.DatabaseError:
            flash("При изменении возникла ошибка", "danger")
            db.connection.rollback()
            return render_template('change_password.html', errors=errors, fields=fields)
    return render_template('change_password.html', errors=errors, fields=fields)


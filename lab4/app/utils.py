from flask import request

error_message = {
        "EMPTY_LOGIN": "Логин не должен быть пустым",
        "EMPTY_PASSWORD": "Пароль не должен быть пустым",
        "EMPTY_NAME": "Фамилия и имя не могут быть пустыми",
        "SHORT_LOGIN": "Логин должен быть не меньше 5 символов",
        "INCORRECT_LOGIN": "Логин должен состоять только из латинских букв и цифр",
        "SHORT_PASSWORD": "Пароль должен быть не меньше 8 символов",
        "LONG_PASSWORD": "Пароль должен быть не более 128 символов",
        "INCORRECT_PASSWORD": '''Пароль должен состоять из латинских или кириллических букв, содержать только арабские цифры и допустимые символы: ~!?@#$%^&*_-+()[]{}></\|"'.,:;''',
        "ALPHA_IN_PASSWORD": "Пароль должен содержать как минимум одну заглавную букву",
        "LITERAL_IN_PASSWORD": "Пароль должен содержать как минимум одну строчную букву",
        "DIGITS_IN_PASSWORD": "Пароль должен содержать как минимум одну цифру",
        "WRONG_PASSWORD": "Неверный пароль",
        "WRONG_CONFIRMATION_PASSWORD": "Пароль должен быть таким же"
}

formdata_fields = ["login", "password", "last_name", "first_name", "middle_name", "role_id"]

# Получение только необходимых параметров из формы запроса
def extract_form():
    result = {}
    for name in formdata_fields:
        result[name] = request.form.get(name) or None
    return result

# Валидация формы создания пользователя
def create_user_validation(params):
    PERMITTED_LOGIN = "abcdefghijklmnopqrstuvwxyz1234567890"
    errors_res = {
        "login": None,
        "password": None,
        "last_name": None,
        "first_name": None,
        "isvalidate": 1,
    }

    login = params.get("login")
    if login is None:
        errors_res["login"] = error_message["EMPTY_LOGIN"]
        errors_res["isvalidate"] = 0
    elif len(login) < 5:
        errors_res["login"] = error_message["SHORT_LOGIN"]
        errors_res["isvalidate"] = 0
    else:
        for char in login:
             if PERMITTED_LOGIN.find(char.lower()) == -1:
                 errors_res["login"] = error_message["INCORRECT_LOGIN"]
                 errors_res["isvalidate"] = 0
                 break
             
    if params.get("last_name") is None:
        errors_res["last_name"] = error_message["EMPTY_NAME"]
        errors_res["isvalidate"] = 0

    if params.get("first_name") is None:
        errors_res["first_name"] = error_message["EMPTY_NAME"]
        errors_res["isvalidate"] = 0

    checked_password = check_password(params.get('password'))
    if not checked_password is None:
        errors_res["password"] = checked_password
        errors_res["isvalidate"] = 0

    return errors_res

# Валидация формы редактирования пользователя
def edit_user_validation(params):
    PERMITTED_LOGIN = "abcdefghijklmnopqrstuvwxyz1234567890"
    errors_res = {
        "login": None,
        "last_name": None,
        "first_name": None,
        "isvalidate": 1,
    }

    login = params.get("login")
    if login is None:
        errors_res["login"] = error_message["EMPTY_LOGIN"]
        errors_res["isvalidate"] = 0
    elif len(login) < 5:
        errors_res["login"] = error_message["SHORT_LOGIN"]
        errors_res["isvalidate"] = 0
    else:
        for char in login:
             if PERMITTED_LOGIN.find(char.lower()) == -1:
                 errors_res["login"] = error_message["INCORRECT_LOGIN"]
                 errors_res["isvalidate"] = 0
                 break
             

    if params.get("last_name") is None:
        errors_res["last_name"] = error_message["EMPTY_NAME"]
        errors_res["isvalidate"] = 0


    if params.get("first_name") is None:
        errors_res["first_name"] = error_message["EMPTY_NAME"]
        errors_res["isvalidate"] = 0

    return errors_res

PERMITTED_PASSWORD = '''abcdefghijklmnopqrstuvwxyzабвгдеёжзийклмнопрстуфхцчшщъыьэюя1234567890~!?@#$%^&*_-+()[]{}></\|"'.,:;'''

#Валидация пароля
def check_password(password):
    errors_res = None
    count_upper_letters = 0
    count_lower_letters = 0
    count_digits = 0
    if password is None:
        errors_res = error_message["EMPTY_PASSWORD"]
    elif len(password) < 8:
        errors_res = error_message["SHORT_PASSWORD"]
    elif len(password) > 128:
        errors_res = error_message["LONG_PASSWORD"]
    elif password.find(" ") > -1:
        errors_res = error_message["INCORRECT_PASSWORD"]
    else:
        for char in password:
            if PERMITTED_PASSWORD.find(char.lower()) == -1:
                errors_res = error_message["INCORRECT_PASSWORD"]
                break
            elif char.isalpha():
                if char.isupper():
                    count_upper_letters += 1
                else:
                    count_lower_letters += 1
            elif char.isdigit():
                count_digits += 1
        if count_upper_letters < 1:
            errors_res = error_message["ALPHA_IN_PASSWORD"]
        elif count_lower_letters < 1:
            errors_res = error_message["LITERAL_IN_PASSWORD"]
        elif count_digits < 1:
            errors_res = error_message["DIGITS_IN_PASSWORD"]
    return errors_res


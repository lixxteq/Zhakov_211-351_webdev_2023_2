from flask import Flask, render_template, request, make_response

app = Flask(__name__)
application = app

@app.route('/')
def index():
    return render_template('index.html')

@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404

@app.route('/headers')
def headers():
    return render_template("headers.html")
    
@app.route('/args')
def args():
    return render_template("args.html")

@app.route('/cookies')
def cookies():
    resp = make_response(render_template("cookies.html"))
    if 'example' in request.cookies: 
        resp.set_cookie('example', '123', expires = 0)
    else:
        resp.set_cookie('example', '123')
    return resp

@app.route('/form', methods = ['GET', 'POST'])
def form():
    return render_template("form.html")

def transformation_text(kind, nums_phone_number):
    result = ''
    if kind == '+7':
        result = f'8-{nums_phone_number[1:4]}-{nums_phone_number[4:7]}-{nums_phone_number[7:9]}-{nums_phone_number[9:]}'
    elif kind == '8':
        result = f'8-{nums_phone_number[1:4]}-{nums_phone_number[4:7]}-{nums_phone_number[7:9]}-{nums_phone_number[9:]}'
    elif kind == '10':
        result = f'8-{nums_phone_number[0:3]}-{nums_phone_number[3:6]}-{nums_phone_number[6:8]}-{nums_phone_number[8:]}'
    return result

@app.route('/validate_phone', methods = ['GET', 'POST'])
def validate_phone():
    symbols = ['+', '.', ')', '(', '-', ' ']
    error = False
    phone_number = None
    formatted = ''

    if request.method == 'POST':
        digit_array = []
        phone_number = request.form.get('phone_number')
        for e in phone_number:
            if e.isdigit():
                digit_array.append(e)
            elif e not in symbols:
                error = 'Недопустимый ввод. В номере телефона встречаются недопустимые символы.'
                break
        if not error:
            if len(digit_array) == 11 and digit_array[0] in ['7', '8']:
                formatted = '-'.join(['8', ''.join(digit_array[1:4]), ''.join(digit_array[4:7]), ''.join(digit_array[7:9]), ''.join(digit_array[9:11])])
            elif len(digit_array) == 10:
                formatted = '-'.join(['8', ''.join(digit_array[0:3]), ''.join(digit_array[3:6]), ''.join(digit_array[6:8]), ''.join(digit_array[8:10])])
            else:
                error = 'Недопустимый ввод. Неверное количество цифр.'
    return render_template('validate_phone.html', phone_number=phone_number, error=error, formatted=formatted)

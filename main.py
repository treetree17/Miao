import pymssql
from flask import Flask, render_template, request

import database

database.init_database()

CONFIG = {
    "host": '127.0.0.1:1433',
    "user": 'sa',
    "pwd": 'DATABASE2023',
    'db': 'MiaoMiao'
}

conn = pymssql.connect(CONFIG['host'], CONFIG['user'], CONFIG['pwd'])

if conn:
    print("连接成功!")
cursor = conn.cursor()
app = Flask(__name__)
uid = "user"
cid = "cat"


class Login():
    def __init__(self):
        super().__init__()


@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("register.html")


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        userid = request.form.get('UID')
        username = request.form.get('Uname')
        password = request.form.get('password')
        department = request.form.get('department')
        major = request.form.get('major')
        info1 = {
            'UID': userid,
            'UNAME': username,
            'PASSWORD': password,
            'DEPARTMENT': department,
            'MAJOR': major,
        }

        ans = database.signup(info1)
        if ans:
            return render_template('login.html')
    else:
        return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    global uid
    if request.method == 'POST':
        userid = request.form.get('UID')
        uid = userid
        password = request.form.get('password')
        info = {
            'ID': userid,
            'PASSWORD': password
        }
        user = database.signin(info)
        if user['class'] == 'admin':
            print('登录成功！')
            return render_template('widget_1.html')
        if user['class'] == 'user':
            print('登录成功！')
            print(uid)
            return render_template('widget_2.html')
    else:
        print('登录失败！')


@app.route('/my-endpoint1', methods=['POST'])
def my_endpoint1():
    return render_template('login.html')


@app.route('/my-endpoint2', methods=['POST'])
def my_endpoint2():
    return render_template('register.html')


@app.route('/apply', methods=['POST'])
def apply():
    global cid
    rowId_param = request.form.get('rowId')
    cid = rowId_param
    res = database.apply_cat(cid, uid)
    print(res)
    return "已提交申请"


@app.route('/cat')
def cat():
    rows1 = database.cat_info()
    return render_template('widget_2.html', rows1=rows1)


@app.route('/apply_info')
def apply_info():
    rows2 = database.get_apply(uid)
    return render_template('widget_2.html', rows2=rows2)


app.run(port=8080)

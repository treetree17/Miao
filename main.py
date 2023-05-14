import pymssql
from flask import Flask, render_template, request

import database

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
            print('成功')
            # 注册成功跳转到登录页面
            return render_template('login.html')
    else:
        # 否则依然返回注册页面
        print('注册失败')
        return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        userid = request.form.get('UID')
        password = request.form.get('password')
        info = {
            'ID': userid,
            'PASSWORD': password
        }

        user = database.signin(info)
        if user is not None:
            print('登录成功！')
        else:
            print('登录失败!')


@app.route('/my-endpoint1', methods=['POST'])
def my_endpoint1():
    return render_template('login.html')


@app.route('/my-endpoint2', methods=['POST'])
def my_endpoint2():
    return render_template('register.html')


app.run(port=8080)

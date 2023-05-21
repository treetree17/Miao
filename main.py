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


@app.route('/cat2')
def cat2():
    rows1 = database.cat_info()
    return render_template('widget_1.html', rows1=rows1)


@app.route('/delete_cat', methods=['POST'])
def delete_cat():
    cat_id = request.form['cat_id']  # 从前端获取要删除的猫咪编号
    res = database.delete_cat(cat_id)
    if res:
        return 'Success'
    else:
        return 'Error'


@app.route('/user')
def user():
    rows2 = database.user_info()
    return render_template('widget_1.html', rows2=rows2)


@app.route('/apply_info')
def apply_info():
    rows2 = database.get_apply(uid)
    return render_template('widget_2.html', rows2=rows2)


@app.route('/edit_user', methods=['GET', 'POST'])
def edit_user():
    if request.method == 'POST':
        username = request.form.get('Uname')
        password = request.form.get('password')
        password_new = request.form.get('password_new')
        department = request.form.get('department')
        major = request.form.get('major')
        info = {
            'UID': uid,
            'UNAME': username,
            'PASSWORD': password,
            'PASSWORD_NEW': password_new,
            'DEPARTMENT': department,
            'MAJOR': major,
        }
        res = database.update_info(info)
        if res:
            return '更新成功！'
        else:
            return '更新失败！'
    else:
        return '更新失败！'


@app.route('/edit_cat', methods=['GET', 'POST'])
def edit_cat():
    if request.method == 'POST':
        CID = request.form.get('CID')
        Cname = request.form.get('cname')
        gender = request.form.get('gender')
        color = request.form.get('color')
        activity_area = request.form.get('activity_area')
        status = request.form.get('status')
        info = {
            'CID': CID,
            'CNAME': Cname,
            'GENDER': gender,
            'COLOR': color,
            'ACTIVITY_AREA': activity_area,
            'STATUS': status,
        }
        res = database.update_cat(info)
        if res:
            return '更新成功！'
        else:
            return '更新失败！'
    else:
        return '更新失败！'


@app.route('/add_cat', methods=['GET', 'POST'])
def add_cat():
    if request.method == 'POST':
        CID = request.form.get('CID2')
        cname = request.form.get('Cname2')
        gender = request.form.get('gender2')
        color = request.form.get('color2')
        activity_area = request.form.get('activity_area2')
        status = request.form.get('status2')
        info = {
            'CID': CID,
            'CNAME': cname,
            'CSEX': gender,
            'COLOR': color,
            'ACTIVITY_AREA': activity_area,
            'STATUS': status,
        }
        print(info)
        res = database.new_cat(info)
        if res:
            return '添加成功！'
        else:
            return '添加失败！'
    else:
        return '添加失败！'


@app.route('/edit_user2', methods=['GET', 'POST'])
def edit_user2():
    if request.method == 'POST':
        userid = request.form.get('UID')
        username = request.form.get('Uname')
        password = request.form.get('password')
        password_new = request.form.get('password_new')
        department = request.form.get('department')
        major = request.form.get('major')
        info = {
            'UID': userid,
            'UNAME': username,
            'PASSWORD': password,
            'PASSWORD_NEW': password_new,
            'DEPARTMENT': department,
            'MAJOR': major,
        }
        res = database.update_info(info)
        if res:
            return '更新成功！'
        else:
            return '更新失败！'
    else:
        return '更新失败！'


@app.route('/apply_info2', methods=['GET', 'POST'])
def apply_info2():
    rows3 = database.apply_info()
    return render_template('widget_1.html', rows3=rows3)


@app.route('/approve1', methods=['POST'])
def approve1():
    rowId_param = request.form.get('rowId')
    rowId_param2 = request.form.get('rowId2')
    res = database.approveP(rowId_param2, rowId_param)
    return "审批通过"


@app.route('/approve2', methods=['POST'])
def approve2():
    rowId_param = request.form.get('rowId')
    rowId_param2 = request.form.get('rowId2')
    res = database.approveNP(rowId_param2, rowId_param)
    return "审批未通过"


@app.route('/approve_log', methods=['GET', 'POST'])
def approve_log():
    rows4 = database.approve_info()
    return render_template('widget_1.html', rows4=rows4)


app.run(port=8080)

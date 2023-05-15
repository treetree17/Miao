import time
import pymssql

CONFIG = {
    "host": '127.0.0.1:1433',
    "user": 'sa',
    "pwd": 'DATABASE2023',
    'db': 'MiaoMiao'
}


# 检查注册信息
def check_user_info(info: dict) -> dict:
    """
    info = {
            'UID': self.accountInput.text(),
            'UNAME': self.nameInput.text(),
            'EMAIL':self.emailInput.text(),
            'PASSWORD': self.passwordInput.text(),
            'REPASSWORD': self.repPasswordInput.text(),
            'DEPARTMENT': self.deptInput.text(),
            'MAJOR': self.majorInput.text(),
        }
    返回 ans = {
        'res':'fail|success',
        'reason':''
    }
    """
    ans = {
        'res': 'fail',
        'reason': ''
    }
    if len(info['UID']) != 8:
        ans['reason'] = 'ID长度必须为8'
        return ans
    if not info['UID'].isalnum():
        ans['reason'] = 'ID存在非法字符'
        return ans
    if info['PASSWORD'] != info['REPASSWORD']:
        ans['reason'] = '两次输入密码不一致'
        return ans
    if not info['EMAIL'].contains("@"):
        ans['reason'] = '邮箱格式输入错误'
        return ans
    if len(info['DEPARTMENT']) > 20:
        ans['reason'] = '学院名称超过20'
        return ans
    if len(info['MAJOR']) > 20:
        ans['reason'] = '专业名称超过20'
        return ans
    ans['res'] = 'success'
    return ans


# 去掉字符串末尾的0
def remove_blank(val):
    if type(val) is not str:
        return val
    while len(val) != 0 and val[-1] == ' ':
        val = val[:-1]
    return val


# 把book元组转换为list
def tuple_to_list(val: list):
    """
    传入tuple列表把里面的tuple都转换为list同时去掉字符串里的空格
    """
    ans = []
    for tuple_ in val:
        temp = []
        for item in tuple_:
            temp.append(item)
            if type(temp[-1]) is str:
                temp[-1] = remove_blank(temp[-1])
        ans.append(temp)
    return ans


# 将元组列表转换为字典
def convert(val: list):
    if len(val) == 0:
        return None
    val = val[0]
    # 如果是user
    if len(val) == 4:
        ans = {
            'class': 'user',
            'UID': remove_blank(val[0]),
            'UNAME': remove_blank(val[1]),
            'DEPARTMENT': remove_blank(val[2]),
            'MAJOR': remove_blank(val[3]),
        }
    else:
        ans = {
            'class': 'admin',
            'AID': remove_blank(val[0])
        }
    return ans


# 数据库初始化
def init_database():
    try:
        conn = pymssql.connect(CONFIG['host'], CONFIG['user'], CONFIG['pwd'])
        cursor = conn.cursor()
        conn.autocommit(True)
        cursor.execute('''CREATE DATABASE MiaoMiao''')
        conn.autocommit(False)
        cursor.execute('''
        USE MiaoMiao
        
        CREATE TABLE administrator(
         AID char(5) PRIMARY KEY,
         password nvarchar(50)
        )

        CREATE TABLE EndUser(
         UID char(8) PRIMARY KEY,
         Uname nvarchar(50),
         password nvarchar(50),
         department nvarchar(50),
         major nvarchar(50)
        )

        CREATE TABLE cat(
         CID char(5) PRIMARY KEY,
         cname nvarchar(50),
         csex nchar(1),
         ccolor nvarchar(50),
         clocation nvarchar(50),
         cstatus char(2),
        )

        CREATE TABLE apply(
         CID char(5),
         UID char(8),
         apply_time nvarchar(50),
         PRIMARY KEY(UID,CID)
        )

        CREATE TABLE approve(
         CID char(5),
         UID char(8),
         approve_time nvarchar(50),
         result char(4),
         PRIMARY KEY(UID,CID)
        )

        INSERT
        INTO administrator
        VALUES('admin', '123456')
        ''')
        conn.commit()
    except Exception as e:
        print('Init fall 如果数据库已经成功初始化则无视此条警告')
        print(e)
    finally:
        if conn:
            conn.close()


# 注册
def signup(user_message: dict) -> bool:
    """
    传入以下格式的字典
    user_message{
        'UID': str,
        'UNAME': str,
        'PASSWORD': str,
        'DEPARTMENT': str,
        'MAJOR': str,
    }
    """
    res = True
    try:
        conn = pymssql.connect(CONFIG['host'], CONFIG['user'], CONFIG['pwd'], CONFIG['db'])
        cursor = conn.cursor()
        cursor.execute('''
            SELECT *
            FROM EndUser
            WHERE UID = %s
            ''', (user_message['UID']))
        if len(cursor.fetchall()) != 0:
            raise Exception('用户已存在!')
        cursor.execute('''
        INSERT
        INTO EndUser
        VALUES(%s, %s, %s, %s,%s)
        ''', (
            user_message['UID'],
            user_message['UNAME'],
            user_message['PASSWORD'],
            user_message['DEPARTMENT'],
            user_message['MAJOR']
        ))
        conn.commit()
    except Exception as e:
        print('Signup error!')
        print(e)
        res = False
    finally:
        if conn:
            conn.close()
        return res


# 登录
def signin(user_message: dict) -> dict:
    """
    传入以下格式的字典
    user_message{
        'ID': str,
        'PASSWORD': str
    }
    如果管理员用户存在返回以下字典
    {
        'class': 'admin'
        'AID': str
    }
    如果学生用户存在返回以下格式的字典
    {
        'class': 'user'
        'UID': str,
        'UNAME': str,
        'DEPARTMENT': str,
        'MAJOR': str,
    }
    否则返回None
    """
    ans = None
    try:
        conn = pymssql.connect(CONFIG['host'], CONFIG['user'], CONFIG['pwd'], CONFIG['db'])
        cursor = conn.cursor()
        # 现在administrator表内匹配
        cursor.execute('''
        SELECT AID
        FROM administrator
        WHERE AID = %s AND PASSWORD=%s
        ''', (
            user_message['ID'],
            user_message['PASSWORD']
        ))
        temp = cursor.fetchall()
        # 管理员表内没有找到则在student表内匹配
        if len(temp) == 0:
            cursor.execute('''
            SELECT UID, UNAME, DEPARTMENT, MAJOR
            FROM EndUser
            WHERE UID = %s AND PASSWORD = %s
            ''', (
                user_message['ID'],
                user_message['PASSWORD']
            ))
            temp = cursor.fetchall()
        ans = temp
        conn.commit()
    except Exception as e:
        print('Signin error!')
        print(e)
    finally:
        if conn:
            conn.close()
        return convert(ans)


# 更新学生信息
def update_student(user_message: dict) -> bool:
    '''
    传入字典格式如下
    user_message{
        'UID': str,
        'PASSWORD': str,
        'UNAME': str,
        'DEPARTMENT': str,
        'MAJOR': str,
    }
    返回bool
    '''
    try:
        res = True
        conn = pymssql.connect(CONFIG['host'], CONFIG['user'], CONFIG['pwd'], CONFIG['db'])
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE EndUser
            SET UNAME=%s, DEPARTMENT=%s, MAJOR=%s
            WHERE UID=%s
            ''', (
            user_message['UNAME'],
            user_message['DEPARTMENT'],
            user_message['MAJOR'],
            user_message['UID']
        ))
        if 'PASSWORD' in user_message:
            cursor.execute('''
            UPDATE EndUser
            SET PASSWORD = %s
            WHERE UID = %s
            ''', (
                user_message['PASSWORD'],
                user_message['UID']
            ))
        conn.commit()
    except Exception as e:
        print('Update error!')
        print(e)
        res = False
    finally:
        if conn:
            conn.close()
        return res


# 获取学生信息
def get_student_info(UID: str) -> dict:
    """
    传入UID
    返回user_message{
        'UID': str,
        'PASSWORD': str,
        'UNAME': str,
        'DEPARTMENT': str,
        'MAJOR': str,
    }
    """
    try:
        conn = pymssql.connect(CONFIG['host'], CONFIG['user'], CONFIG['pwd'], CONFIG['db'])
        cursor = conn.cursor()
        cursor.execute('''
            SELECT UID, UNAME, DEPARTMENT, MAJOR
            FROM EndUser
            WHERE UID=%s
            ''', UID)
        ans = cursor.fetchall()
    except Exception as e:
        print(e)
        print('get user info error')
    finally:
        if conn:
            conn.close()
        return convert(ans)


# 查找学生
def search_student(info: str) -> list:
    try:
        res = []
        val = info.split()
        val = [(i, '%' + i + '%') for i in val]
        conn = pymssql.connect(CONFIG['host'], CONFIG['user'], CONFIG['pwd'], CONFIG['db'])
        cursor = conn.cursor()
        # 显示所有学生信息
        if info == 'ID/姓名' or info == '':
            cursor.execute('''
            SELECT UID, UNAME, DEPARTMENT, MAJOR
            FROM EndUser
            ''')
            res += cursor.fetchall()
        else:
            # 按条件查找
            for i in val:
                cursor.execute('''
                SELECT UID, UNAME, DEPARTMENT, MAJOR
                FROM EndUser
                WHERE UID = %s OR UNAME LIKE %s
                ''', i)
                res += cursor.fetchall()
        res = list(set(res))
        temp = []
        for i in res:
            temp_ = []
            for j in i:
                temp_.append(remove_blank(j))
            temp.append(temp_)
        res = temp
    except Exception as e:
        print('Search user error!')
        print(e)
        res = []
    finally:
        if conn:
            conn.close()
        return res


# 获取学生的领养申请信息
def get_apply(UID: str):
    try:
        conn = pymssql.connect(CONFIG['host'], CONFIG['user'], CONFIG['pwd'], CONFIG['db'])
        cursor = conn.cursor()
        cursor.execute('''
                SELECT cat.CID, cname, apply_time, approve_time, result
                FROM apply, approve, cat
                WHERE approve.UID = %s AND approve.CID = apply.CID AND cat.CID = apply.CID AND cat.CID = approve.CID
            ''', (UID,))
        res = cursor.fetchall()
        print(res)
    except Exception as e:
        print('get apply error!')
        print(e)
        res = []
    finally:
        if conn:
            conn.close()
        return res


# 审批通过
def approveP(CID: str, UID: str) -> bool:
    '''
        传入CID, UID，删除apply表内的记录在approve表内新建记录
    返回bool型
    '''
    try:
        res = True
        conn = pymssql.connect(CONFIG['host'], CONFIG['user'], CONFIG['pwd'], CONFIG['db'])
        cursor = conn.cursor()
        # 先把申请时间，喵咪状态等信息找出
        cursor.execute('''
        SELECT apply_time, cstatus 
        FROM  apply, cat
        WHERE UID = %s AND  apply.CID = %s AND apply.CID = cat.CID
        ''', (UID, CID))
        CAT_mes = cursor.fetchall()
        CSTATUS = CAT_mes[0][1]
        if CSTATUS == 'H': CSTATUS = 'A'
        APPLY_TIME = CAT_mes[0][0]
        APPROVE_TIME = time.strftime("%Y-%m-%d-%H:%M")

        # cat表内cstatus状态更新，删除apply表内的记录，把记录插入approve表
        cursor.execute('''
        UPDATE cat
        SET cstatus = %s
        WHERE CID = %s
        DELETE
        FROM apply
        WHERE UID=%s AND CID=%s
        INSERT
        INTO approve
        VALUES(%s, %s, %s, %s， %d)
        ''', (CSTATUS, CID, UID, CID, CID, UID, APPLY_TIME, APPROVE_TIME, 1))
        conn.commit()
    except Exception as e:
        print('Approve error!')
        print(e)
        res = False
    finally:
        if conn:
            conn.close()
        return res


# 审批未通过
def approveNP(CID: str, UID: str) -> bool:
    '''
        传入CID, UID，删除apply表内的记录在approve表内新建记录
    返回bool型
    '''
    try:
        res = True
        conn = pymssql.connect(CONFIG['host'], CONFIG['user'], CONFIG['pwd'], CONFIG['db'])
        cursor = conn.cursor()
        # 先把申请时间，喵咪状态等信息找出
        cursor.execute('''
        SELECT apply_time, cstatus 
        FROM  apply, cat
        WHERE UID = %s AND  apply.CID = %s AND apply.CID = cat.CID
        ''', (UID, CID))
        CAT_mes = cursor.fetchall()
        CSTATUS = CAT_mes[0][1]
        APPLY_TIME = CAT_mes[0][0]
        APPROVE_TIME = time.strftime("%Y-%m-%d-%H:%M")

        # 删除apply表内的记录，把记录插入approve表
        cursor.execute('''
        DELETE
        FROM apply
        WHERE UID=%s AND CID=%s
        INSERT
        INTO approve
        VALUES(%s, %s, %s, %s， %d)
        ''', (UID, CID, CID, UID, APPLY_TIME, APPROVE_TIME, 0))
        conn.commit()
    except Exception as e:
        print('Approve error!')
        print(e)
        res = False
    finally:
        if conn:
            conn.close()
        return res


# 获取审批历史记录
def get_approve(ID: str, CID: bool = False) -> list:
    '''
    传入SID
    返回[...]
    '''
    try:
        conn = pymssql.connect(CONFIG['host'], CONFIG['user'], CONFIG['pwd'], CONFIG['db'])
        cursor = conn.cursor()
        if ID == '' or ID == 'ID/姓名':
            cursor.execute('''
                SELECT UID, cat.CID, came, APPLY_TIME, APPROVE_TIME, RESULT
                FROM approve, cat
                WHERE cat.CID = approve.CID
                ORDER BY APPROVE_TIME
            ''')
        elif CID:
            cursor.execute('''
                SELECT UID, cat.CID, cname, APPLY_TIME, APPROVE_TIME, RESULT
                FROM approve, cat 
                WHERE approve.CID = %s AND cat.CID=approve.CID
                ORDER BY APPROVE_TIME
            ''', (ID,))
        else:
            cursor.execute('''
                SELECT UID, cat.CID, cname, APPLY_TIME, APPROVE_TIME, RESULT
                FROM approve, cat
                WHERE UID = %s AND cat.CID = log.CID
                ORDER BY APPROVE_TIME
            ''', (ID,))
        res = cursor.fetchall()
    except Exception as e:
        print('get approve error!')
        print(e)
        res = []
    finally:
        if conn:
            conn.close()
        temp = []
        for i in res:
            temp_ = []
            for j in i:
                temp_.append(remove_blank(j))
            temp.append(temp_)
        return temp


# 加入新猫猫
def new_cat(cat_info: dict) -> bool:
    '''
    传入以下格式的字典
    TABLE cat(
         CID char(5) PRIMARY KEY,
         Cname nvarchar(50),
         Csex nchar(1),
         Ccolor nvarchar(50),
         Clocation nvarchar(50),
         Cstatus char(2),
         Csterilization char(1),
         Story nvarchar(200)
        )
    返回bool
    '''
    res = True
    try:
        conn = pymssql.connect(CONFIG['host'], CONFIG['user'], CONFIG['pwd'], CONFIG['db'])
        cursor = conn.cursor()
        cursor.execute('''
            SELECT *
            FROM cat
            WHERE CID = %s
            ''', (cat_info['CID']))
        if len(cursor.fetchall()) != 0:
            raise Exception('猫猫ID已存在!')
        # 插入新猫猫
        cursor.execute('''
        INSERT
        INTO cat
        VALUES(%s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            cat_info['CID'],
            cat_info['CNAME'],
            cat_info['Csex'],
            cat_info['Ccolor'],
            cat_info['Clocation'],
            cat_info['Cstatus'],
            cat_info['Csterilization'],
            cat_info['Story']
        ))
        conn.commit()
    except Exception as e:
        print('add cat error!')
        print(e)
        res = False
    finally:
        if conn:
            conn.close()
        return res


# 获取新猫猫详细信息
def get_cat_info(CID: str) -> dict:
    '''
    传入CID
    TABLE Cat(
         CID char(5) PRIMARY KEY,
         Cname nvarchar(50),
         Csex nchar(1),
         Ccolor nvarchar(50),
         Clocation nvarchar(50),
         Cstatus char(2),
         Csterilization char(1),
         Story nvarchar(200)
        )
    }
    '''
    try:
        conn = pymssql.connect(CONFIG['host'], CONFIG['user'], CONFIG['pwd'], CONFIG['db'])
        cursor = conn.cursor()
        # 获取book表内的书本信息
        cursor.execute('''
            SELECT *
            FROM cat
            WHERE CID=%s
            ''', (CID))
        res = cursor.fetchall()
        if len(res) == 0:
            raise Exception('查无此猫猫')

        # 把列表转换为字典
        res = list(res[0])
        key_list = ['CID', 'CNAME', 'Csex', 'Ccolor', 'Clocation', 'Cstatus', 'Csterilization', 'Story']
        ans = {}
        for i, key in zip(res, key_list):
            ans[key] = i
            if type(i) is str:
                ans[key] = remove_blank(i)
        res = ans
    except Exception as e:
        print('get cat info error!')
        print(e)
        res = None
    finally:
        if conn:
            conn.close()
        return res


# 获取所有猫猫信息
def cat_info():
    conn = pymssql.connect(CONFIG['host'], CONFIG['user'], CONFIG['pwd'], CONFIG['db'])
    cursor = conn.cursor()
    cursor.execute('''
            SELECT *
            FROM cat
            ''')
    rows = cursor.fetchall()
    conn.close()
    return rows


# 更新猫猫信息
def update_cat(cat_info: dict) -> bool:
    """
    传入以下格式的字典
    TABLE cat(
         CID char(5) PRIMARY KEY,
         Cname nvarchar(50),
         Csex nchar(1),
         Ccolor nvarchar(50),
         Clocation nvarchar(50),
         Cstatus char(2),
         Csterilization char(1),
         Story nvarchar(200)
        )
    返回bool
    """
    try:
        res = True
        conn = pymssql.connect(CONFIG['host'], CONFIG['user'], CONFIG['pwd'], CONFIG['db'])
        cursor = conn.cursor()
        # 更新book表
        cursor.execute('''
            UPDATE book
            SET CNAME=%s, Csex=%s, Ccolor=%s, Clocation=%s, Cstatus=%s, Csterilization=%s, Story=%s
            WHERE CID=%s
            ''', (
            cat_info['CNAME'],
            cat_info['Csex'],
            cat_info['Ccolor'],
            cat_info['Clocation'],
            cat_info['Cstatus'],
            cat_info['Csterilization'],
            cat_info['Story'],
            cat_info['CID']
        ))

        conn.commit()
    except Exception as e:
        print('Update cat error!')
        print(e)
        res = False
    finally:
        if conn:
            conn.close()
        return res


# 删除猫猫
def delete_cat(CID: str) -> bool:
    '''
    传入CID
    返回bool
    会删除cat,apply,approve 表内所有对应的记录
    '''
    try:
        res = True
        conn = pymssql.connect(CONFIG['host'], CONFIG['user'], CONFIG['pwd'], CONFIG['db'])
        cursor = conn.cursor()
        cursor.execute('''
            DELETE
            FROM cat
            WHERE CID = %s
            DELETE
            FROM apply
            WHERE CID = %s
            DELETE
            FROM approve
            WHERE CID = %s
            ''', (CID, CID, CID))
        conn.commit()
    except Exception as e:
        print('delete cat error!')
        print(e)
        res = False
    finally:
        if conn:
            conn.close()
        return res


# 搜索猫猫
def search_cat(info: str, restrict: str, UID: str = '') -> list:
    '''
    传入搜索信息，并指明CID...进行查找，如果传入SID则匹配这个学生的借书状态
    返回[...]
    '''
    try:
        res = []
        conn = pymssql.connect(CONFIG['host'], CONFIG['user'], CONFIG['pwd'], CONFIG['db'])
        cursor = conn.cursor()

        if info == 'ID/Cname/Csex/Clocation/Cstatus' or info == '':
            cursor.execute('''
            SELECT *
            FROM cat
            ''')
        elif restrict == 'CID':
            cursor.execute('''
            SELECT *
            FROM cat
            WHERE CID = %s
            ''', info)
            res = tuple_to_list(cursor.fetchall())

    except Exception as e:
        print('Search error!')
        print(e)
        res = []
    finally:
        if conn:
            conn.close()
        return res


# 申请领养
def apply_cat(CID: str, UID: str) -> bool:
    try:
        res = True
        conn = pymssql.connect(CONFIG['host'], CONFIG['user'], CONFIG['pwd'], CONFIG['db'])
        cursor = conn.cursor()
        BORROW_DATE = time.strftime("%Y-%m-%d-%H:%M")
        cursor.execute('''
        INSERT
        INTO apply
        VALUES(%s, %s, %s)
        ''', (CID, UID, BORROW_DATE))
        conn.commit()
    except Exception as e:
        print('apply error!')
        print(e)
        res = False
    finally:
        if conn:
            conn.close()
        return res


# 密码   为了调试方便就先不加密了
def encrypt(val):
    import hashlib
    h = hashlib.sha256()
    password = val
    h.update(bytes(password, encoding='UTF-8'))
    result = h.hexdigest()
    # 注释下面一行即可加密
    result = val
    return result

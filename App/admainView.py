import os
import time

from PIL import Image
from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from werkzeug.utils import secure_filename

from App.ext import db, socketio
from App.models import User, Admin, Order, Item

admin = Blueprint('admin', __name__)

UPLOAD_FOLDER = 'D:\\PycharmWorkSpace\\bishe0\\static\\face'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'mp3'])

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
else:
    pass


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# 登录
@admin.route('/adminLogin/', methods=['POST', 'GET'])
def admin_login():
    if request.method == "GET":
        return render_template('adminLogin.html')

    if request.method == 'POST':
        admin_name = request.form.get('username')
        password = request.form.get('password')
        # 判断用户名和密码是否填写
        if not all([admin_name, password]):
            msg = '* 请填写好完整的信息'
            return render_template('adminLogin.html', msg=msg)
        # 核对用户名和密码是否一致
        admin = Admin.query.filter_by(admin_name=admin_name, password=password).first()
        # 如果用户名和密码一致
        if admin:
            # 向session中写入相应的数据
            session['admin_name'] = admin.admin_name
            session['admin_id'] = admin.admin_id
            session['admin_face'] = admin.admin_face
            return redirect(url_for('admin.manage_user'))
        # 如果用户名和密码不一致返回登录页面,并给提示信息
        else:
            msg = '* 用户名或者密码不一致'
            return render_template('adminLogin.html', msg=msg)
    return render_template('adminLogin.html')


# 注册  上传图像
@admin.route('/adminRegister/', methods=['POST', 'GET'])
def admin_Register():
    if request.method == 'GET':
        return render_template("adminRegister.html")

    if request.method == 'POST':
        admin_name = request.form.get('username')
        pwd1 = request.form.get('pwd1')
        pwd2 = request.form.get('pwd2')
        code = request.form.get('code')
        image_code = session['image_code']
        print(admin_name)
        flag = True
        if not all([admin_name, pwd1, pwd2, code]):
            msg, flag = '* 请填写完整信息', False
        elif len(admin_name) > 16:
            msg, flag = '* 用户名太长', False
        elif pwd1 != pwd2:
            msg, flag = '* 两次密码不一致', False
        elif code.lower() != image_code.lower():
            msg, flag = '* 验证码错误', False
        if not flag:
            return render_template('adminRegister.html', msg=msg)

        admin = Admin.query.filter(Admin.admin_name == admin_name).first()
        if admin:
            msg = '用户名已经存在'
            return render_template('adminRegister.html', msg=msg)

        url = ''
        file = request.files['file']
        if file and allowed_file(file.filename):
            IconName = secure_filename(file.filename)
            filename = admin_name + IconName
            url = '/static/face/' + filename
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            pathname = os.path.join(UPLOAD_FOLDER, filename)
            img = Image.open(pathname)
            # 创建缩
            img.thumbnail((128, 128))
            img.save(pathname)

        admin = Admin(admin_name=admin_name, password=pwd1, admin_face=url)
        db.session.add(admin)
        db.session.commit()
        return 'ok'


# 退出
@admin.route('/adminLogout/', methods=['GET'])
def admin_logout():
    if request.method == 'GET':
        # 清空session
        session['admin_id'] = ''
        session['admin_name'] = ''
        # 跳转到登录页面
        return redirect(url_for('admin.manage_user'))


# 按用户信誉度查看用户
@admin.route('/manageUser/', methods=['POST', 'GET'])
def manage_user():
    admin_id = session.get('admin_id')
    if not admin_id:
        return render_template('manageUser.html', users='', admin='')
    admin = Admin.query.get(admin_id)
    users = User.query.filter(User.user_status == 1).order_by(User.credit).all()
    if users and admin:
        return render_template('manageUser.html', users=users, admin=admin)
    return render_template('manageUser.html', users='', admin='')


# 删除用户   改变用户发布商品的状态为0
@admin.route('/deleteUser/<user_id>', methods=['POST', 'GET'])
def delete_user(user_id):
    user = User.query.get(user_id)
    user.user_status = 0
    db.session.commit()
    items = Item.query.filter(Item.user_id == user_id)
    for item in items:
        item.status = -1

    print(items)
    db.session.add_all(items)
    db.session.commit()
    return redirect(url_for('admin.manage_user'))


# 查看用户交易
@admin.route('/order/<user_id>', methods=['POST', 'GET'])
def admin_order(user_id):
    admin_name = session['admin_name']
    admin_face = session['admin_face']
    admin_id = session.get('admin_id')
    admin = Admin.query.get(admin_id)
    orders = Order.query.filter(Order.user2_id == user_id).all()
    if not orders:
        msg = '该用户暂时没有交易！'
        return render_template('adminOrder.html', msg=msg, admin_name=admin_name, admin_face=admin_face,admin=admin)
    return render_template('adminOrder.html', orders=orders, admin_name=admin_name, admin_face=admin_face,admin='')


# 审核用户发布的商品
@admin.route('/checkItem/', methods=['POST', 'GET'])
def check_item():
    admin_id = session['admin_id']
    admin_name = session['admin_name']
    admin_face = session['admin_face']
    if not admin_id:
        return render_template('adminCheckItem.html', admin_face='', items='')

    items = Item.query.filter(Item.status == 1).all()
    if items:
        return render_template('adminCheckItem.html', admin_name=admin_name, admin_face=admin_face, items=items)

    return render_template('adminCheckItem.html', admin_face='', items='')


# 未过审商品数目
@admin.route('/checkCount/', methods=['POST', 'GET'])
def check_count():
    items = Item.query.filter(Item.status == 1).all()
    count = len(items)
    return jsonify({'check_count': count})


# 商品过审   通过socketIO刷新前台
@admin.route('/passCheck/<item_id>', methods=['POST', 'GET'])
def pass_check(item_id):
    item = Item.query.get(item_id)
    item.status = 2
    db.session.commit()

    # 刷新客index页面
    name_space='/index'
    event_name = "freshen"
    broadcasted_data = {'code': 200}
    socketio.emit(event_name, broadcasted_data, broadcast=True, namespace=name_space)
    return redirect(url_for('admin.check_item'))

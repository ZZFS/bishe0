# coding:utf-8
import datetime
import json
import os
import random
import re
import time
from datetime import date
import uuid
from io import BytesIO
from flask_mail import Mail
from PIL import Image
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, app, make_response, \
    current_app
from flask_mail import Message
from sqlalchemy import or_
from werkzeug.utils import secure_filename

from App.ext import db, socketio
from App.validate_code import get_verify_code
from .models import User, Item, ShopCar, Order, Search, Provincial, Reduce, ChatMsg, History
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr

user = Blueprint('user', __name__)

UPLOAD_FOLDER = 'D:\\PycharmWorkSpace\\bishe0\\static\\face'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'mp3'])

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
else:
    pass


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@user.route('/createAll')
def create():
    db.create_all()
    return 'ok'


# 主页  推荐商品  从search中取出用户搜索记录list
# 使用多条件查询  然后用卖方的信誉度排序
@user.route('/index')
def index():
    user_id = session.get('user_id')
    if not user_id:
        items = Item.query.filter(Item.status == 2).order_by(Item.item_id.desc()).all()[0:8]
        return render_template('index.html', items=items)
    # 通过查询次数推荐
    if user_id:
        # 用户查询次数较高
        search1 = Search.query.filter(Search.user_id == user_id, Search.search_status == 1).order_by(
            Search.search_count.desc()).slice(0, 4).all()
        # 推荐之前没有的商品
        search2 = Search.query.filter(Search.user_id == user_id).filter(Search.search_status == 0).order_by \
            (Search.search_id.desc()).all()
        searchs = search2 + search1
        items = []
        for search in searchs:
            print(search.content)
            items += Item.query.filter(Item.itemName.like('%' + search.content + '%'), Item.status == 2). \
                         all()[0:13]

        items2 = []
        for item in items:
            if item not in items2:
                items2.append(item)

        print(items2)
        # 如果用户没有搜索记录
        if not items:
            items = Item.query.filter(Item.status == 2).order_by(Item.item_id.desc()).all()[0:8]
            return render_template('index.html', items=items, user_id=user_id, msg='商品推荐')
        return render_template('index.html', items=items2, user_id=user_id, msg='商品推荐')


# 登录
@user.route('/login/', methods=['post', 'get'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # 判断用户名和密码是否填写
        if not all([username, password]):
            msg = '* 请填写好完整的信息'
            return render_template('login.html', msg=msg)
        # 核对用户名和密码是否一致
        user = User.query.filter_by(username=username, password=password, user_status=1).first()
        # 如果用户名和密码一致
        if user:
            # 向session中写入相应的数据
            session['user_id'] = user.user_id
            session['username'] = user.username
            session['user_pic'] = user.Icon
            return redirect(url_for('user.index'))
        # 如果用户名和密码不一致返回登录页面,并给提示信息
        else:
            msg = '* 用户名或者密码不一致'
            return render_template('login.html', msg=msg)


# 注册
@user.route('/register/', methods=['post', 'get'])
def register():
    if request.method == 'GET':
        return render_template("register.html")
    if request.method == 'POST':
        username = request.form.get('username')
        pwd1 = request.form.get('pwd1')
        pwd2 = request.form.get('pwd2')
        email = request.form.get('email')
        code = request.form.get('code')
        image_code = session['image_code']
        # phone = request.form.get('phone')
        flag = True

        if not all([username, pwd1, pwd2, email, code]):
            msg, flag = '* 请填写完整信息', False
            return render_template('register.html', msg=msg)
        if len(username) > 16:
            msg, flag = '* 用户名太长', False
            return render_template('register.html', msg=msg)
        if pwd1 != pwd2:
            msg, flag = '* 两次密码不一致', False
            return render_template('register.html', msg=msg)
        if code.lower() != image_code.lower():
            msg, flag = '* 验证码错误', False
            return render_template('register.html', msg=msg)
        if not flag:
            return render_template('register.html', msg=msg)

        u = User.query.filter(User.username == username).first()
        if u:
            msg = '用户名已经存在'
            return render_template('register.html', msg=msg)

        reg_time = time.strftime("%Y-%m-%d", time.localtime())
        user = User(username=username, password=pwd1, email=email, reg_time=reg_time)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('user.login'))


# 检查用户是否存在
@user.route('/validateUser/')
def validate_user():
    username = request.args.get('username')
    user = User.query.filter(User.username == username).first()
    if user:
        return jsonify({'Code': 200, 'msg': '用户已存在'})
    return jsonify({'Code': 500})


# 获取验证码
@user.route('/code')
def get_code():
    # 返回图片和 验证码
    image, code = get_verify_code()
    # 将验证码图片以二进制形式写入在内存中，防止将图片都放在文件夹中，占用大量磁盘
    buf = BytesIO()
    image.save(buf, 'jpeg')
    buf_str = buf.getvalue()
    # 把二进制作为response发回前端，并设置首部字段
    response = make_response(buf_str)
    response.headers['Content-Type'] = 'image/gif'
    # 将验证码字符串储存在session中
    session['image_code'] = code
    return response  # 返回一个响应


# 退出
@user.route('/logout/', methods=['GET'])
def logout():
    """
    退出登录
    """
    if request.method == 'GET':
        # 清空session
        session['user_id'] = ''
        session['username'] = ''
        # 跳转到登录页面
        return redirect(url_for('user.index'))


# 查看个人信息  修改信息
@user.route('/userInfo/', methods=['GET', 'POST'])
def userInfo():
    if request.method == 'GET':
        username = session.get('username')
        user_id = session.get('user_id')
        if not all([username, user_id]):
            return redirect(url_for('user.login'))
        user = User.query.get(user_id)
        session['password'] = user.password
        return render_template("userInfo.html", user=user)

    if request.method == 'POST':
        username = request.form.get("username")
        phone = request.form.get("phone")
        email = request.form.get("email")
        work = request.form.get("work")
        address1 = request.form.get("address1")
        address2 = request.form.get("address2")
        password = session['password']
        user_id = session['user_id']
        user = User.query.get(user_id)
        user.username = username
        user.address1 = address1
        user.address2 = address2
        user.work = work
        user.email = email
        user.phone = phone
        db.session.commit()
        return jsonify({'resultCode': '200'})


# 用户上传图像
@user.route('/uploadFace', methods=['POST'])
def upload_face():
    # request请求中是否包含文件域
    if 'file' not in request.files:
        return jsonify({'resultCode': '500'})
    file = request.files['file']
    if file.filename == '':
        return jsonify({'resultCode': '500'})
    if file and allowed_file(file.filename):
        username = session['username']
        IconName = secure_filename(file.filename)
        filename = username + IconName
        user_id = session['user_id']
        user = User.query.get(user_id)
        url = '/static/face/' + filename
        user.Icon = url
        session['user_pic'] = url
        db.session.commit()
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        pathname = os.path.join(UPLOAD_FOLDER, filename)
        img = Image.open(pathname)
        # 创建缩
        img.thumbnail((128, 128))
        img.save(pathname)
        return jsonify({'resultCode': '200', 'url': url})


# 修改密码
@user.route('/modifyPwd/', methods=['POST', 'GET'])
def modify_pwd():
    if request.method == 'GET':
        return render_template('modifyPwd.html')

    if request.method == 'POST':
        email = request.form.get('email')
        pwd1 = request.form.get('password1')
        pwd2 = request.form.get('password2')
        verify_code = request.form.get('code')

        user = User.query.filter(User.email == email).first()
        mailCode = session['mailCode']

        if not all([email, pwd1, pwd2, verify_code]):
            return render_template('modifyPwd.html', msg='*请输入完整信息')
        if pwd1 != pwd2:
            return render_template('modifyPwd.html', msg='*两次密码不一致')
        if pwd1 == pwd2:
            if verify_code.lower() != mailCode.lower():
                return render_template('modifyPwd.html', msg='*验证码不正确')
            else:
                user.password = pwd1
                db.session.commit()
                return render_template('modifyPwd.html', msg='修改密码成功')

    return render_template('modifyPwd.html')


# 邮箱验证码
@user.route('/sendMailCode/', methods=['POST', "GET"])
def send_mailCode():
    sender = '2277813013@qq.com'
    recipient = request.form.get("recipient")
    random_sample = random.sample('1234567890abcdefghijklmnopqrstuvwxyz', 4)
    code = ''
    for i in random_sample:
        code += i

    session['mailCode'] = code
    msg = "易淘二手交易网站验证码：" + code
    message = MIMEText(msg, 'plain', 'utf-8')
    message['From'] = formataddr(["易淘二手商城", sender])

    subject = '易淘二手交易网站通知'
    message['Subject'] = Header(subject, 'utf-8')

    smtpObj = smtplib.SMTP('smtp.qq.com', port=25)
    smtpObj.login(user=sender, password='dklweoxkokbjeaff')

    smtpObj.sendmail(sender, recipient, message.as_string())
    return jsonify({'Code': '200'})


# 添加商品到购物车
@user.route('/addShopcar/', methods=['GET'])
def add_shopcar():
    item_id = request.args.get('item_id')
    item = Item.query.get(item_id)
    user_id = session['user_id']
    if not user_id:
        return redirect(url_for('user.login'))
    user = User.query.get(user_id)
    if item.count > 0:
        # 当用户购买类似的产品是，修改用户搜索内容
        itemName = item.itemName
        search = Search.query.filter(Search.user_id == user_id, Search.content.like('%' + itemName + '%')).first()
        if search:
            search.search_status = 1
            db.session.commit()

        shopcar = ShopCar.query.filter(ShopCar.item_id == item_id).first()
        if shopcar:
            shopcar.count = shopcar.count + 1
            db.session.commit()
            return jsonify({'Code': 200, 'msg': '商品添加成功'})
        shopcar = ShopCar(pic1=item.pic1, itemName=item.itemName, price=item.price, user_id=user_id, item_id=item_id)
        db.session.add(shopcar)
        db.session.commit()
        return jsonify({'Code': 200, 'msg': '商品添加成功'})
    return jsonify({'Code': 500, 'msg': '商品库存不足'})


# 查看购物车
@user.route('/shopCar/', methods=['GET'])
def shopCar():
    user_id = session['user_id']
    if not user_id:
        return redirect(url_for('user.login'))
    itemList = ShopCar.query.filter_by(user_id=user_id).all()
    if itemList:
        return render_template("shopcar.html", itemList=itemList)

    return render_template("shopcar.html", itemList='')


# 改变购物车中商品数量
@user.route('/changeCount/', methods=['GET', "POST"])
def change_count():
    ShopCar_id = request.form.get('shopCar_id')
    count = request.form.get('count')
    print(count)
    print(ShopCar_id)
    shopCar = ShopCar.query.get(ShopCar_id)
    shopCar.count = count
    db.session.commit()
    return jsonify({'Code': 200})


# 结算购物车
@user.route('/CloseShopCar/', methods=['GET'])
def Close_shopCar():
    # 从购物车中取商品
    ShopCar_id = request.args.get('shopCar_id')
    print(ShopCar_id)
    shopCar = ShopCar.query.get(ShopCar_id)
    item_id = shopCar.item_id
    # 从item表中取正常商品
    item = Item.query.filter(Item.item_id == item_id, Item.status == 2).first()
    if item:
        # 商品库存不足
        if item.count < shopCar.count:
            msg = "商品仅剩" + str(item.count) + "件"
            return jsonify({'Code': 500, 'msg': msg})

        # 商品库存充足
        # 修改item表中库存数量
        item.count = item.count - shopCar.count
        db.session.commit()

        user1_id = session['user_id']
        user2_id = item.user_id  # 卖方id
        user1 = User.query.get(user1_id)
        user2 = User.query.get(user2_id)
        uid = str(uuid.uuid4())
        Order_uuid = ''.join(uid.split('-'))
        orderTime = time.strftime("%Y-%m-%d", time.localtime())
        itemName = item.itemName
        phone = user1.phone

        # 修改搜索记录
        search = Search.query.filter(Search.user_id == user1_id, Search.content.like('%' + itemName + '%'),
                                     Search.search_status == 0).first()
        if search:
            search.search_status = 1
            db.session.commit()

        # 库存足够时  添加订单
        order = Order(pic1=item.pic1, order_uuid=Order_uuid, price=item.price, condition=item.condition,
                      address1=user1.address1, address2=user2.address2, status="已发货", phone=phone,
                      user1_id=user1_id, user2_id=item.user_id, time=orderTime, itemName=itemName)
        db.session.add(order)
        db.session.commit()

        # 从购物车中删除商品
        db.session.delete(shopCar)
        db.session.commit()
        return jsonify({'Code': 200, 'msg': '商品购买成功'})
    return jsonify({'Code': 500, 'msg': '购买失败'})


# 删除购物车中商品
@user.route('/deleteShopCar/<ShopCar_id>', methods=['GET'])
def delete_ShopCar(ShopCar_id):
    shopCar = ShopCar.query.get(ShopCar_id)
    db.session.delete(shopCar)
    db.session.commit()
    return redirect(url_for('user.shopCar'))


# # 上传商品   取出信息  上传图片 创建对象  插入数据库
@user.route('/uploadItem/', methods=['GET', 'POST'])
def uploadItem():
    if request.method == 'GET':
        return render_template("uploadItem1.html")
    if request.method == 'POST':
        user_id = session['user_id']
        if not user_id:
            redirect(url_for('user.login'))
        user = User.query.get(user_id)
        itemname = request.form.get('itemname')
        price = request.form.get('price')
        config = request.form.get('config')
        detail = request.form.get('detail')
        categary = request.form.get('categary')
        condition = request.form.get('condition')
        count = request.form.get('count')
        user_credit = user.credit
        # 上传图片
        file1 = request.files.get('file1')
        file2 = request.files.get('file2')
        file3 = request.files.get('file3')
        if not all([file1, file2, file3]):
            return jsonify({'Code': 500, 'msg': '请填上传三张商品图片'})
        files = [file1, file2, file3]
        if not all([itemname, price, detail, categary, condition, count]):
            return jsonify({'Code': 500, 'msg': '请填写完整信息'})

        print(type(price))
        pattern = re.compile(r'^[-+]?[-0-9]\d*\.\d*|[-+]?\.?[0-9]\d*$')
        result = pattern.match(price)
        if not result:
            return jsonify({'Code': 500, 'msg': '请填写正确的价格'})
        if float(price) < 0:
            return jsonify({'Code': 500, 'msg': '商品价格有误'})

        price = float(price)
        # 保存图片
        urls = []
        for file in files:
            if file and allowed_file(file.filename):
                picname = secure_filename(file.filename)
                urls.append('/static/itemPic/' + picname)
                # 上传图片
                FOLDER = 'D:\\PycharmWorkSpace\\bishe0\\static\\itemPic'
                file.save(os.path.join(FOLDER, picname))

        # 保存视频
        video = request.files.get('file4')
        print(video)
        v_url = ''
        if video:
            videoName = secure_filename(video.filename)
            print(videoName)
            VIDEO_FOLDER = 'D:\\PycharmWorkSpace\\bishe0\\static\\video'
            file.save(os.path.join(VIDEO_FOLDER, videoName))
            v_url = '/static/video/' + videoName
            print(v_url)

        itemTime = time.strftime("%Y-%m-%d", time.localtime())
        print(urls)
        # 存贮到数据库
        item = Item(itemName=itemname, price=price, detail=detail, count=count,
                    categary=categary, status='1', condition=condition,
                    pic1=urls[0], pic2=urls[1], pic3=urls[2], user_id=user_id, time=itemTime,
                    config=config, user_credit=user_credit, video=v_url)

        db.session.add(item)
        db.session.commit()
        return jsonify({'Code': 200, 'pic': urls})

    return jsonify({'Code': 500})


# 上传视频
@user.route('/uploadcVideo', methods=['POST', 'GET'])
def uploadc_Video():
    pass


# 上传商品图片
@user.route('/uploadPic', methods=['POST'])
def upload_Pic():
    # request请求中是否包含文件域
    if 'file' not in request.files:
        return jsonify({'resultCode': '500'})
    file = request.files['file']
    if file.filename == '':
        return jsonify({'resultCode': '500'})
    if file and allowed_file(file.filename):
        username = session['username']
        IconName = secure_filename(file.filename)
        filename = username + IconName
        user_id = session['user_id']
        user = User.query.get(user_id)
        url = '/static/face/' + filename
        user.Icon = url
        db.session.commit()
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        pathname = os.path.join(UPLOAD_FOLDER, filename)
        img = Image.open(pathname)
        # 创建缩
        img.thumbnail((128, 128))
        img.save(pathname)
        return jsonify({'resultCode': '200', 'url': url})


# 查看已发布的商品
@user.route('/publishedItem/', methods=['GET', 'POST'])
def publishedItem():
    user_id = session['user_id']
    if not user_id:
        redirect(url_for('user.login'))
    items = Item.query.filter(Item.user_id == user_id).all()
    if not items:
        return render_template("publishedItem.html", items=items, msg='你还没有上传商品')
    return render_template("publishedItem.html", items=items)


# 删除已发布的商品
@user.route('/deleteItem/<item_id>', methods=['GET', 'POST'])
def delete_Item(item_id):
    item = Item.query.get(item_id)
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for('user.publishedItem'))


# 查看已发布商品的详情  修改商品详情
@user.route('/reviseItem/', methods=['GET', 'POST'])
def revise_item():
    if request.method == 'GET':
        item_id = request.args.get('item_id')
        session['item_id'] = item_id
        item = Item.query.get(item_id)
        return render_template("reviseItem.html", item=item)

    if request.method == 'POST':
        itemName = request.form.get('itemName')
        price = request.form.get('price')
        detail = request.form.get('detail')
        condition = request.form.get('condition')
        address1 = request.form.get('address1')
        config = request.form.get('config')
        item_id = session['item_id']

        # 获取商品
        item = Item.query.get(item_id)
        item.itemName = itemName
        oldPrice = item.price
        item.price = price
        item.detail = detail
        item.condition = condition
        item.address1 = address1
        item.config = config

        db.session.commit()

        if float(price) < oldPrice:
            # 通过邮件通知所有用户
            reduces = Reduce.query.filter_by(item_id=item_id).all()
            emails = []
            for reduce in reduces:
                emails.append(reduce.email)

            gap = oldPrice - float(price)
            msg = "您关注的" + item.itemName + "，已经降价" + str(gap) + "元 !"
            sendMail(msg, emails)
        return jsonify({'resultCode': '200'})

    return render_template("reviseItem.html", item='')


def sendMail(msg, emails):
    sender = '2277813013@qq.com'  # 邮件发送者的邮箱地址

    # 三个参数：第一个为邮件正文文本内容，第二个 plain 设置文本格式，第三个 utf-8 设置编码
    message = MIMEText(msg, 'plain', 'utf-8')
    message['From'] = formataddr(["易淘二手商城", sender])  # 发送者

    subject = '易淘二手交易网站通知'
    message['Subject'] = Header(subject, 'utf-8')  # 邮件的主题

    smtpObj = smtplib.SMTP('smtp.qq.com', port=25)
    smtpObj.login(user=sender, password='dklweoxkokbjeaff')  # password并不是邮箱的密码，而是开启邮箱的授权码
    for recipient in emails:
        smtpObj.sendmail(sender, recipient, message.as_string())  # 发送邮件


# 添加商品到订单  user1  买方 user2卖方
@user.route('/addOrder/', methods=['GET'])
def add_Order():
    item_id = request.args.get('item_id')
    item = Item.query.get(item_id)
    if item:
        user1_id = session['user_id']
        user2_id = item.user_id
        user1 = User.query.get(user1_id)
        user2 = User.query.get(user2_id)
        uid = str(uuid.uuid4())
        Order_uuid = ''.join(uid.split('-'))
        orderTime = time.strftime("%Y-%m-%d", time.localtime())
        itemName = item.itemName
        phone = user1.phone

        # 修改搜索记录
        search = Search.query.filter(Search.user_id == user1_id, Search.content.like('%' + itemName + '%')).first()
        if search and search.search_status == 0:
            search.search_status = 1
            db.session.commit()
        # 判断商品库存
        itemCount = item.count
        itemCount = itemCount - 1
        if itemCount <= 0:
            item.status = 0
            db.session.commit()
            return jsonify({'Code': 500, 'msg': '库存不足'})

        item.count = itemCount
        db.session.commit()
        order = Order(pic1=item.pic1, order_uuid=Order_uuid, price=item.price, condition=item.condition,
                      address1=user1.address1, address2=user2.address2, status="已发货", phone=phone,
                      user1_id=user1_id, user2_id=item.user_id, time=orderTime, itemName=itemName)
        db.session.add(order)
        db.session.commit()
        return jsonify({'Code': 200, 'msg': '商品购买成功'})
    return jsonify({'Code': 500, 'msg': '商品购买失败'})


# 添加减价通知通知   返回商品详情
@user.route('/reduce/', methods=['GET'])
def item_reduce():
    user_id = session['user_id']
    item_id = request.args.get('item_id')
    user = User.query.filter_by(user_id=user_id).first()
    reduce = Reduce.query.filter_by(user_id=user_id, item_id=item_id).first()

    if reduce:
        return jsonify({'Code': 200, 'msg': '关注成功'})
    else:
        reduce = Reduce(user_id=user_id, item_id=item_id, email=user.email)
        db.session.add(reduce)
        db.session.commit()
        return jsonify({'Code': 200, 'msg': '关注成功'})


# 查看商品详情
@user.route('/detail/<item_id>', methods=['GET'])
def detail(item_id):
    item = Item.query.get(item_id)
    item.visit_count = item.visit_count + 1
    db.session.commit()
    # 获取卖方信息
    user2_id = item.user_id
    user = User.query.get(user2_id)

    # 买方信息
    user1_id = session.get('user_id')
    time = date.today()
    history = History.query.filter_by(item_id=item_id, user_id=user1_id).first()
    if history:
        history.time = time
        db.session.commit()
    else:
        history = History(item_id=item_id, user_id=user1_id,
                          item_pic=item.pic1, item_name=item.itemName, item_categary=item.categary, time=time)
        print(item.pic1)
        db.session.add(history)
        db.session.commit()

    search = Search.query.filter(Search.user_id == user1_id, Search.content.like('%' + item.categary + '%')).first()
    if search:
        print(search)
        search.search_count = search.search_count + 1
        db.session.commit()
    else:
        search = Search(content=item.categary, user_id=user1_id)
        db.session.add(search)
        db.session.commit()
    return render_template("detail.html", item=item, user=user)


# 查看订单
@user.route('/order/', methods=['GET'])
def order():
    user_id = session['user_id']
    page = int(request.args.get('page') or 1)

    OrderList = Order.query.filter_by(user1_id=user_id).paginate(page, 6)
    for i in OrderList.items:
        print(i)
    return render_template("order.html", pagination=OrderList)


# 查看订单详情
@user.route('/orderInfo/<order_id>', methods=['GET'])
def orderInfo(order_id):
    order = Order.query.get(order_id)
    return render_template("orderInfo.html", order=order)


# 删除订单
@user.route('/deleteOrder/<order_id>', methods=['GET'])
def delete_order(order_id):
    order = Order.query.get(order_id)
    db.session.delete(order)
    db.session.commit()
    return redirect(url_for('user.order'))


# 评价订单  获取用户评分  user表中 统计总评分   统计交易次数  计算信誉度
@user.route('/evaluate/', methods=['GET', 'POST'])
def evaluate():
    order_id = request.form.get('order_id')
    start = request.form.get('start')

    order = Order.query.get(order_id)
    order.start = start
    db.session.commit()

    user2_id = order.user2_id
    user = User.query.get(user2_id)
    user.trans_count = user.trans_count + 1
    user.start_cout = user.start_cout + int(start)
    a = (user.start_cout / user.trans_count) * 20
    user.credit = round(a, 2)
    db.session.commit()
    return jsonify({'Code': 200})


# 评价订单
@user.route('/comment/', methods=['GET', 'POST'])
def comment():
    order_id = request.form.get('order_id')
    comment = request.form.get('comment')
    order = Order.query.get(order_id)
    order.comment = comment
    order.status = "已收货"
    db.session.commit()
    return jsonify({'Code': 200})


# 搜索商品  将搜索的内容存到search表中   统计搜索的次数 有相同的搜索内容该次数自增
# 如果无返回内容   做标记
@user.route('/search/', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        content = request.form.get('search')

        if not content:
            return redirect(url_for('user.index'))
        user_id = session['user_id']
        items = Item.query.filter(Item.itemName.like('%' + content + '%')).all()

        search = Search.query.filter(Search.user_id == user_id, Search.content.like('%' + content + '%')).first()
        if search:
            search.search_count = search.search_count + 1
            db.session.commit()

        # 没有相同的搜索记录
        else:
            if items:
                search = Search(content=content, user_id=user_id, search_status=1)
                db.session.add(search)
                db.session.commit()
            else:
                search = Search(content=content, user_id=user_id)
                db.session.add(search)
                db.session.commit()
        return render_template("index.html", items=items, msg='搜索结果', user_id=user_id)
    return render_template("index.html", items='', msg='搜索结果', user_id=session['user_id'])


# 查看商品列表
@user.route('/itemList/<categary>', methods=['GET'])
def itemList(categary):
    session['categary'] = categary
    return redirect(url_for('user.paginate'))


# 分页查询
@user.route('/paginate/', methods=['GET'])
def paginate():
    categary = session['categary']
    page = int(request.args.get('page') or 1)
    # 页码page，每页显示10条
    pageObj = Item.query.filter_by(categary=categary, status=2).order_by(Item.user_credit.desc()).paginate(page, 8)
    return render_template('itemList.html', pagination=pageObj, categary=categary)


@user.route('/test/', methods=['GET'])
def test():
    return render_template("itemList.html")


# 查看已上传物品
@user.route('/uploadInfo/', methods=['GET'])
def uploadInfo():
    return render_template("uploadInfo.html")


@user.route('/page')
def page():
    # 传递的页码数量
    page = int(request.args.get('page') or 1)

    # 页码page，每页显示10条
    pageObj = Item.query.filter_by(categary='a').paginate(page, 5)
    return render_template('goodIndex.html', pagination=pageObj)


# 修改商品信息
@user.route('/reviseItem/', methods=['GET', 'POST'])
def reviseItem():
    return render_template("reviseItem.html")


# 及时通讯
# {'name': '/static/face/abofang.jpg', 'msg': 'ww', 'item_id': 56}
name_space = '/abcd'
msgs = []


# 以用户名决定事件名
# 用户发送消息  其他页面消息提示
@socketio.on('my event', namespace=name_space)
def handle_json(data):
    print('新消息: ' + str(data))
    user_pic = session.get('user_pic')
    user_id = session.get('user_id')
    if not all([user_pic, user_id]):
        return redirect(url_for('user.login'))

    item_id = data['item_id']

    session['item_id'] = item_id
    msg = data['msg']

    # 通过商品id 得到卖方id
    item = Item.query.get(item_id)
    seller_id = item.user_id

    # 将聊天消息查到数据库中
    cur_time = datetime.datetime.now()
    messege = ChatMsg(user1_id=user_id, user_pic=user_pic, msg=msg,
                      item_id=item_id, user2_id=seller_id, time=cur_time)
    db.session.add(messege)
    db.session.commit()

    data = {'name': user_pic, 'msg': msg, 'item_id': item_id, 'seller': seller_id}
    print(data)
    msgs.append(data)
    # jsonData =json.dumps(data)
    print('打印所有消息')
    print(msgs)
    # hint ={'seller':seller_id,'item_id':item_id}
    hint = seller_id
    print(hint)
    socketio.emit('response', data, namespace=name_space, broadcast=True)
    socketio.emit('hint', hint, namespace=name_space, broadcast=True)  # 加入用户id用于区分用户


@user.route('/getMsgCount/', methods=['POST', 'GET'])
def get_msgCount():
    print('get_msgCount')
    user_id = request.args.get('user_id')
    print(user_id)
    count = 0
    for countMsg in msgs:
        print(type(countMsg))
        print('sssssss' + str(countMsg['seller']))
        if int(countMsg['seller']) == int(user_id):
            print(countMsg['seller'])
            count += 1
    print(count)
    return jsonify({'code': 200, 'count': count})


# 用js求出消息条数  消息通知   卖方进入聊天界面
# 卖方进入聊天界面
@user.route('/msgHint/', methods=['POST', 'GET'])
def msg_hint():
    user_pic = session.get('user_pic')
    user_id = session.get('user_id')

    msgs = ChatMsg.query.filter(or_(ChatMsg.user1_id == user_id, ChatMsg.user2_id == user_id)).all()
    hintList = []
    for msg in msgs:
        item_id = msg.item_id
        if item_id not in hintList:
            hintList.append(msg.item_id)
    itemList = []

    for hint in hintList:
        item = Item.query.get(hint)
        itemList.append(item)

    print(itemList)
    # 查询商品
    # item=Item.query.get(item_id)
    # return render_template('userChat.html',item=item)
    # user_pic = session['user_pic']
    # msgList = []
    # for msg in msgs:
    #     if msg['name'] == user_pic:
    #         msgList.append(msg)
    # print(msgList)
    # return 'OK'
    print(hintList)
    item = Item.query.get(item_id)
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    return render_template('chatMsg.html', itemList=itemList, item=item, user=user)


# 卖方聊天
@user.route('/sellChat/<item_id>', methods=['POST', 'GET'])
def sellChat(item_id):
    item = Item.query.get(item_id)
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    return render_template("2chat.html", item=item, user=user)


# 加载历史消息
chatMsgs = []


@user.route('/loadMsg/<item_id>', methods=['POST', 'GET'])
def load_msg(item_id):
    if request.method == 'GET':
        jsonData = {'msgs': msgs}
        print("加载历史消息")
        print(jsonData)
        # {'msgs': [{'name': '/static/face/wQQ20190321202911.jpg', 'msg': 'å¥½', 'item_id': 57}]}  jsonData
        # chat_msgs=ChatMsg.query.filter(ChatMsg.item_id==item_id).all()
        # for chat_msg in chat_msgs:
        #     chatItem=

    return jsonify({'Code': 200, 'data': jsonData})


@socketio.on('connect', namespace=name_space)
def connected_msg():
    """socket client event - connected"""
    print('client connected!')


@socketio.on('disconnect', namespace=name_space)
def disconnect_msg():
    """socket client event - disconnected"""
    print('client disconnected!')


# 游览历史列表
@user.route('/historyList')
def historyList():
    user_id = session.get('user_id')
    historys = History.query.filter_by(user_id=user_id)
    return render_template('historyList.html', historys=historys)


# 删除游览历史
@user.route('/delete_history/<h_id>')
def delete_history(h_id):
    history = History.query.get(h_id)
    db.session.delete(history)
    db.session.commit()
    return redirect(url_for('user.historyList'))


# 省市联动
@user.route('/provincial')
def get_provinve():
    provinces = Provincial.query.filter().all()
    p = []
    for province in provinces:
        p.append(province.name)

    print(p)
    return 'ok'

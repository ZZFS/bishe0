from datetime import datetime

from App.ext import db


# 用户模型
class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), unique=True)
    password = db.Column(db.String(32), nullable=False)
    Icon = db.Column(db.String(64), default='/static/face/default.jpg')
    address1 = db.Column(db.String(64), default='')  # 用户发货地址
    address2 = db.Column(db.String(64), default='')  # 用户收货地址
    email = db.Column(db.String(64), nullable=False)
    phone = db.Column(db.String(64), default='')
    credit = db.Column(db.FLOAT, default='60')
    work = db.Column(db.String(64), default='')
    trans_count = db.Column(db.Integer, default=0)  # 评价之后代表交易完成  交易次数加一  统计买方评分  如何计算信誉度
    start_cout = db.Column(db.Integer, default=0)
    user_status = db.Column(db.Integer, default=1)
    reg_time = db.Column(db.String(64), default='')
    # items = db.relationship('Item', backref='user', lazy=True)  # 关系


# 商品模型
class Item(db.Model):
    item_id = db.Column(db.Integer, primary_key=True)
    itemName = db.Column(db.String(64), nullable=False)
    price = db.Column(db.FLOAT, default=0.0)
    detail = db.Column(db.String(64))
    count = db.Column(db.Integer, default=0)
    time = db.Column(db.String(64), default='')
    status = db.Column(db.Integer)  # 0表示该商品不可卖 卖完  用户被管理员踢出
    categary = db.Column(db.String(64))
    condition = db.Column(db.String(64))
    config = db.Column(db.String(64), default='')
    user_credit = db.Column(db.FLOAT, default=0)

    pic1 = db.Column(db.String(64))
    pic2 = db.Column(db.String(64))
    pic3 = db.Column(db.String(64))
    video=db.Column(db.String(64))
    user_id = db.Column(db.Integer)
    visit_count = db.Column(db.Integer, default=0)
    address1 = db.Column(db.String(64))
    # user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))  # 用户主键作为外键


# # 订单模型   买方评价
class Order(db.Model):
    order_id = db.Column(db.Integer, primary_key=True)
    pic1 = db.Column(db.String(64))
    order_uuid = db.Column(db.String(64))
    itemName = db.Column(db.String(64))
    time = db.Column(db.String(64))
    price = db.Column(db.String(64), default='')
    condition = db.Column(db.String(64))
    address1 = db.Column(db.String(64))
    address2 = db.Column(db.String(64))
    status = db.Column(db.String(64))
    phone = db.Column(db.String(64))
    user1_id = db.Column(db.Integer)  # user1  买方
    user2_id = db.Column(db.Integer)  # user2卖方
    start = db.Column(db.Integer, default=-1)
    comment = db.Column(db.String(64), default='')


# 购物车模型
class ShopCar(db.Model):
    ShopCar_id = db.Column(db.Integer, primary_key=True)
    pic1 = db.Column(db.String(64))
    itemName = db.Column(db.String(64))
    price = db.Column(db.FLOAT)
    count = db.Column(db.Integer, default=1)
    user_id = db.Column(db.Integer)
    item_id = db.Column(db.Integer)


# 用户搜索记录
class Search(db.Model):
    search_id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(64))
    user_id = db.Column(db.Integer)
    search_count = db.Column(db.Integer, default=1)
    search_status = db.Column(db.Integer, default=0)  # 1代表查询有结果


# 降价通知
class Reduce(db.Model):
    reduce_id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer)
    email = db.Column(db.String(64))


class Admin(db.Model):
    admin_id = db.Column(db.Integer, primary_key=True)
    admin_name = db.Column(db.String(64), default='')
    password = db.Column(db.String(64), default='')
    admin_face = db.Column(db.String(64), default='')


class Provincial(db.Model):
    pid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))


class City(db.Model):
    c_id = db.Column(db.Integer, primary_key=True)
    c_name = db.Column(db.String(64))
    p_id = db.Column(db.Integer)


# {'name': '/static/face/abofang.jpg', 'msg': 'ww', 'item_id': 56}
# user1  代表买方  user2代表卖方
class ChatMsg(db.Model):
    m_id = db.Column(db.Integer, primary_key=True)
    user_pic = db.Column(db.String(64))
    user1_id = db.Column(db.Integer)
    user2_id = db.Column(db.Integer)
    msg = db.Column(db.String(64))
    item_id = db.Column(db.Integer)
    time = db.Column(db.Date)

    def to_dic(self):
        data = {
            'm_id': self.m_id,
            'user_pic': self.user1_id,
            'user1_id': self.user1_id,
            'user2_id': self.user2_id,
            'msg': self.msg,
            'item_id': self.item_id
        }
        return data


# 游览历史
class History(db.Model):
    h_id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer)
    item_pic=db.Column(db.String(128))
    item_name=db.Column(db.String(64))
    user_id = db.Column(db.Integer)
    time=db.Column(db.Date)
    item_categary=db.Column(db.String(64))
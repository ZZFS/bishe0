# coding:utf-8
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr


def sendMail():
    sender = '2277813013@qq.com'  # 邮件发送者的邮箱地址
    recipient = '1435084930@qq.com'  # 邮件接收者的邮箱地址

    # 三个参数：第一个为邮件正文文本内容，第二个 plain 设置文本格式，第三个 utf-8 设置编码
    mail_msg = """
       <p>Python 邮件发送测试...</p>
       <p><a href="http://www.runoob.com">这是一个链接</a></p>
       """
    message = MIMEText(mail_msg, 'plain', 'utf-8')
    message['From'] = formataddr(["易淘二手商城", sender])  # 发送者

    subject = '易淘二手网站'
    message['Subject'] = Header(subject, 'utf-8')  # 邮件的主题

    smtpObj = smtplib.SMTP('smtp.qq.com', port=25)
    smtpObj.login(user=sender, password='dklweoxkokbjeaff')  # password并不是邮箱的密码，而是开启邮箱的授权码
    print(recipient)
    smtpObj.sendmail(sender, recipient, message.as_string())  # 发送邮件


sendMail()
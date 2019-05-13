import os

# 绝对路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

static_folder = os.path.join(BASE_DIR, 'static')
TEMPLATE_FOLDER = os.path.join(BASE_DIR, 'templates')


def get_db_uri(dbinfo):
    """ database setting """
    ENGINE = dbinfo.get('ENGINE') or 'mysql'

    DRIVER = dbinfo.get('DRIVER') or 'pymysql'

    USER = dbinfo.get('USER') or 'root'

    PASSWORD = dbinfo.get('PASSWORD') or '1234'

    HOST = dbinfo.get('HOST') or 'localhost'

    PORT = dbinfo.get('PORT') or '3306'

    NAME = dbinfo.get('NAME') or 'bishe'

    return "{}+{}://{}:{}@{}:{}/{}".format(ENGINE, DRIVER, USER, PASSWORD, HOST, PORT, NAME)


class Config:
    DEBUG = False

    TESTING = False

    SECRET_KEY = "1234"

    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopConfig(Config):
    """ 开发环境配置 """
    DEBUG = True

    DATABASE = {
        "ENGINE": 'mysql',
        'DRIVER': 'pymysql',
        'USER': 'root',
        'PASSWORD': '1234',
        'HOST': 'localhost',
        'PORT': '3306',
        'NAME': 'bishe'
    }

    SQLALCHEMY_DATABASE_URI = get_db_uri(DATABASE)
    JSON_AS_ASCII = False
    MAIL_SERVE = 'smtp.qq.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = '2277813013@qq.com'
    MAIL_PASSWORD = 'dklweoxkokbjeaff'


class TestingConfig(Config):
    """ 测试环境配置 """
    TESTING = True

    DATABASE = {
        "ENGINE": 'mysql',
        'DRIVER': 'pymysql',
        'USER': 'root',
        'PASSWORD': 'rock1204',
        'HOST': '127.0.0.1',
        'PORT': '3306',
        'NAME': 'bishe'
    }

    SQLALCHEMY_DATABASE_URI = get_db_uri(DATABASE)


class StagingConfig(Config):
    """ 演示环境配置 """
    DATABASE = {
        "ENGINE": 'mysql',
        'DRIVER': 'pymysql',
        'USER': 'root',
        'PASSWORD': 'rock1204',
        'HOST': 'localhost',
        'PORT': '3306',
        'NAME': 'bishe'
    }

    SQLALCHEMY_DATABASE_URI = get_db_uri(DATABASE)


class ProductConfig(Config):
    """ 上线环境配置 """
    DATABASE = {
        "ENGINE": 'mysql',
        'DRIVER': 'pymysql',
        'USER': 'root',
        'PASSWORD': 'rock1204',
        'HOST': '127.0.0.1',
        'PORT': '3306',
        'NAME': 'bishe'
    }

    SQLALCHEMY_DATABASE_URI = get_db_uri(DATABASE)


envs = {
    'develop': DevelopConfig,
    'testing': TestingConfig,
    'staging': StagingConfig,
    'product': ProductConfig
}

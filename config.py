import os
from sqlalchemy import create_engine  


import urllib

class Config(object):
    SECRET_KEY = 'Clave Nueva'
     
    
class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root1234@127.0.0.1/flask_login'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
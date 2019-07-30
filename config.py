import os

class Config(object):
    SECRET_KEY = 'my_secret_key'
    DEBUG ='True'

class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'mysql://root:1234@localhost/flask'
    SQLALCHEMY_TRACK_MODIFICATIONS = False #se coloca en modo false ya que de lo contrario apareceria un Warning


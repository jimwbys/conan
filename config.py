#coding:utf-8
import os
basedir = os.path.abspath(os.path.dirname(__file__))
maindir = 'http://localhost:5000/'

UPLOAD_FOLDER = 'app/static/users/'
ALLOWED_EXTENSIONS = set(['jpg','png','jpeg'])
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir,'conan.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
WTF_CSRF_ENABLED = True
SECRET_KEY = 'fdew324dfdfw232dsfdscs[]d.'

#pagination
POSTS_PER_PAGE = 10
USERS_PER_PAGE = 10

WHOOSH_BASE = os.path.join(basedir, 'search.db')
MAX_SEARCH_RESULTS = 50

#email server
MAIL_SERVER = 'smtp.163.com'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

#administrator list
ADMINS = ['jimwbys@gmail.com']

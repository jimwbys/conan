#coding:utf-8
from flask.ext.wtf import Form
from wtforms import TextField, PasswordField, BooleanField, StringField, TextAreaField
from wtforms.validators import DataRequired, Length, EqualTo
from app.models import User

class LoginForm(Form):
    email = TextField('email', [Length(min=6, max=35),DataRequired()])
    password = PasswordField('password', [DataRequired()])
    remember_me = BooleanField('remember_me', default=False)

class RegisterForm(Form):
    nickname = TextField('nickname', [Length(min=4, max=25),DataRequired()])
    email = TextField('email', [Length(min=6, max=35),DataRequired()])
    password = PasswordField('password', [DataRequired(),
               EqualTo('confirm', message=u"两次键入的密码必须一致")])
    confirm = PasswordField('Repeat Password')

    def validate(self):
        if not Form.validate(self):
            return False
        user_nickname = User.query.filter_by(nickname=self.nickname.data).first()
        user_email = User.query.filter_by(email=self.email.data).first()
        if user_nickname != None:
            self.nickname.errors.append('This nickname is already in use,please choose another one.')
            return False
        if user_email != None:
            self.email.errors.append('This email is already registered,please choose another one.')
            return False
        return True

class EditForm(Form):
    nickname = StringField('nickname', validators=[DataRequired()])
    about_me = TextAreaField('about_me', validators=[Length(min=0,max=150)])

    def __init__(self,original_nickname,*args,**kwargs):
        Form.__init__(self,*args,**kwargs)
        self.original_nickname = original_nickname

    def validate(self):
        if not Form.validate(self):
            return False
        if self.nickname.data == self.original_nickname:
            return True
        if User.query.filter_by(nickname=self.nickname.data).first() != None:
            self.nickname.errors.append('This nickname is already in use,please choose another one.')
            return False
        return True

class PostForm(Form):
    post = StringField('post',validators=[DataRequired()])

class SearchForm(Form):
    search = StringField('search', validators=[DataRequired()])


#coding:utf-8
from app import db, app
import flask.ext.whooshalchemy as whooshalchemy
from jieba.analyse import ChineseAnalyzer

followers = db.Table('followers',db.Column('follower_id',db.Integer,db.ForeignKey('user.id')),
    db.Column('followed_id',db.Integer,db.ForeignKey('user.id')))

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(64), index=True, unique=True)
    avatar = db.Column(db.String(128))
    email = db.Column(db.String(120), index=True, unique=True)
    password = db.Column(db.String(128), index=False)
    regtime = db.Column(db.DateTime)
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(150))
    last_seen = db.Column(db.DateTime)
    followed = db.relationship('User',secondary=followers,primaryjoin=(followers.c.follower_id == id),
               secondaryjoin=(followers.c.followed_id == id), backref=db.backref('followers',lazy='dynamic'),
               lazy='dynamic')

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return unicode(self.id)
        except NameError:
            return str(self.id)

    def __repr__(self):
        return '<User %r>' % (self.nickname)

    def followed_posts(self):
        return Post.query.join(followers, (followers.c.followed_id == Post.user_id)).filter(
            followers.c.follower_id == self.id).order_by(Post.timestamp.desc())

    def followed_users(self):
        return self.followed

    def follow(self,user):
        if not self.is_following(user):
            self.followed.append(user)
            return self

    def unfollow(self,user):
        if self.is_following(user):
            self.followed.remove(user)
            return self

    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

class Post(db.Model):
    __searchable__ = ['body']

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post %r>' % (self.body)

whooshalchemy.whoosh_index(app, Post)






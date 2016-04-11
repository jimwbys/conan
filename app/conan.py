#coding:utf-8
from flask import render_template, flash, redirect, session, url_for, request, g, send_from_directory
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, lm
from forms import LoginForm, RegisterForm, EditForm, PostForm,SearchForm
from models import User, Post
from datetime import datetime
import os
from werkzeug import secure_filename, SharedDataMiddleware
from config import POSTS_PER_PAGE, MAX_SEARCH_RESULTS, USERS_PER_PAGE, maindir

@app.route('/', methods=['GET','POST'])
@app.route('/index', methods=['GET','POST'])
@app.route('/index/<int:page>', methods=['GET','POST'])
@login_required
def index(page=1):
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, timestamp=datetime.utcnow(), author=g.user)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('index'))
    posts = g.user.followed_posts().paginate(page,POSTS_PER_PAGE,False)
    return render_template('index.html',title='Home',form=form,posts=posts)

@app.route('/login', methods=['GET','POST'])
def login():
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.password == form.password.data:
            login_user(user,remember=form.remember_me.data)
            flash('Welcome Back!')
            return redirect(request.args.get("next") or url_for("index"))
        elif user is None:
            flash('The user does not exist!')
        else:
            flash('email and password does not match')
    return render_template('login.html',title='sign in',form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET','POST'])
def register():
    form = RegisterForm()
    if request.method == 'POST' and form.validate():
        user = User(nickname=form.nickname.data,email=form.email.data,password=form.password.data,regtime=datetime.utcnow())
        db.session.add(user)
        db.session.commit()
        db.session.add(user.follow(user))
        db.session.commit()
        flash('Welcome Back!')
        return redirect(url_for('index'))
    return render_template('register.html',title='register',form=form)


@lm.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.before_request
def before_request():
    g.user = current_user
    if g.user.is_authenticated():
        g.user.last_seen = datetime.utcnow()
        db.session.add(g.user)
        db.session.commit()
        g.search_form = SearchForm()


@app.route('/user/<nickname>')
@app.route('/user/<nickname>/<int:page>')
@login_required
def user(nickname, page=1):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash('User %s not found' % nickname)
        return redirect(url_for('index'))
    posts = user.posts.paginate(page, POSTS_PER_PAGE, False)
    return render_template('user.html',user=user,posts=posts)

@app.route('/user/<nickname>/upload',methods=['GET','POST'])
@login_required
def upload(nickname):
    if request.method == 'POST':
        file = request.files['file']
        filename = secure_filename(file.filename)
        if file and '.' in filename and filename.rsplit('.' , 1)[1] in app.config['ALLOWED_EXTENSIONS']:
            path = os.path.join(app.config['UPLOAD_FOLDER'], g.user.nickname)
            path = os.path.join(path, 'avatar')
            if not os.path.exists(path):
                os.makedirs(path)
            file.save(os.path.join(path,filename))
            g.user.avatar = os.path.join(maindir,'static/users/%s/avatar/%s' % (g.user.nickname,filename))
            db.session.add(g.user)
            db.session.commit()
            return redirect('/user/%s' % g.user.nickname)
    return render_template('upload.html')

@app.route('/edit', methods=['GET','POST'])
@login_required
def edit():
    form = EditForm(g.user.nickname)
    if form.validate_on_submit():
        g.user.nickname = form.nickname.data
        g.user.about_me = form.about_me.data
        db.session.add(g.user)
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit'))
    else:
        form.nickname.data = g.user.nickname
        form.about_me.data = g.user.about_me
    return render_template('edit.html',form=form)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

@app.route('/follow/<nickname>')
@login_required
def follow(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash('User %s not found' % nickname)
        return redirect(url_for('index'))
    if user == g.user:
        flash('You cannot follow yourself!')
        return redirect(url_for('user',nickname=nickname))
    u = g.user.follow(user)
    if u is None:
        flash('cannot follow '+nickname+'.')
        return redirect(url_for('user',nickname=nickname))
    db.session.add(u)
    db.session.commit()
    flash('You are now following '+nickname+'!')
    return redirect(url_for('user',nickname=nickname))

@app.route('/unfollow/<nickname>')
@login_required
def unfollow(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash('User %s not found.' % nickname)
        return redirect(url_for('index'))
    if user == g.user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('user',nickname=nickname))
    u = g.user.unfollow(user)
    if u is None:
        flash('Cannot unfollow '+nickname+'.')
        return redirect(url_for('user',nickname))
    db.session.add(u)
    db.session.commit()
    flash('You have stopped following '+nickname+'.')
    return redirect(url_for('user',nickname=nickname))

@app.route('/search', methods=['POST'])
@login_required
def search():
    if not g.search_form.validate_on_submit():
        return redirect(url_for('index'))
    return redirect(url_for('search_results/', query=g.search_form.search.data))

@app.route('/search_result/<query>')
@login_required
def search_results(query):
    results = Post.query.whoosh_search(query, MAX_SEARCH_RESULTS).all()
    return render_template('search_results.html',query=query, results=results)

@app.route('/delete/<int:id>')
@login_required
def delete(id):
    post = Post.query.get(id)
    if post is None:
        flash('Post not found.')
        return redirect(url_for('index'))
    if post.author.id != g.user.id:
        flash('You cannot delete this post.')
        return(url_for('index'))
    db.session.delete(post)
    db.session.commit()
    flash('The post has been deleted!')
    return redirect(url_for('index'))

@app.route('/relation/<nickname>/<relate>')
@app.route('/relation/<nickname>/<relate>/<int:page>')
@login_required
def followers(relate,nickname,page=1):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash("The user is not found!")
        return redirect(url_for('index'))
    if relate == 'followers':
        people = user.followers.paginate(page,USERS_PER_PAGE,False)
    elif relate == 'followed':
        people = user.followed.paginate(page,USERS_PER_PAGE,False)
    return render_template('userfollow.html',title='people',users=people,relate=relate)

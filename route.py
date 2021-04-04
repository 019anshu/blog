from flask import Flask, render_template, flash, redirect, session, url_for, request
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import *
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
import os

app=Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///Blogpost.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Blogpost(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    blogtitle = db.Column(db.String(255), nullable=False)
    blogcontent = db.Column(db.String(1000), nullable=False)

    dateposted = db.Column(db.DateTime, nullable= False, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self) -> str:
        return f"Blogpost('{self.blogtitle}', '{self.dateposted}')"

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Blogpost', backref='author', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class SignupForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken, Please choose another one!')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken, Please choose another one!')

class NewpostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post' )

@app.route('/')
def homeh():
    return redirect(url_for('home'))

@app.route('/home')
def home():
    allblog = Blogpost.query.all()
    return render_template("home.html",  title="Home", allblog=allblog)

@app.route('/about')
def about():
    return render_template("about.html", title="About")

@app.route('/blogs')
def blogs():
    allblog = Blogpost.query.all()
    return render_template("blogs.html", title="Blogs", allblog=allblog)

@app.route('/blogs/<id>',  methods=['GET', 'POST'])
def showblog(id):
    blog = Blogpost.query.get_or_404(id)
    return render_template("showblog.html",title= blog.blogtitle, blog = blog)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form= LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user and bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('home'))                
            else:
                flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template("login.html", title="Log In", form=form, name=session.get('blogtitle'))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/account')
@login_required
def account():
    return render_template("account.html", title="Account", current_user=current_user)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form= SignupForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user= User(username=form.username.data, email=form.email.data, password=hashed_password)
            db.session.add(user)
            db.session.commit()
            flash(f'{form.username.data}! Your account has been successfully created! You may proceed to Log In', 'success')
            return redirect(url_for('login'))
    return render_template("signup.html", title="Sign Up", form=form)

@app.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form= NewpostForm()
    if request.method == 'POST':
        if form.validate_on_submit:
            title = form.title.data
            content = form.content.data
            blog = Blogpost(blogtitle= title, blogcontent= content, author= current_user)
            db.session.add(blog)
            db.session.commit()
            flash("Posted a new Blog successfully!")
            return redirect(url_for('home'))
    return render_template('create.html', title="New Post", form=form, name=session.get('title'))
    


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', title="Error 404"), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html', title="Error 500"), 500   

if __name__ == '__main__':  
    app.run(debug=True) 

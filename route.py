from flask import Flask, render_template, flash, redirect, session, url_for, request
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import *
import os

app=Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///blogpost.db"
app.config['SQLALCHEMY_TRACK_MOD    IFICATIONS'] = False
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

bootstrap = Bootstrap(app)
db = SQLAlchemy(app)

class blogpost(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    blogtitle = db.Column(db.String(255), nullable=False)
    blogcontent = db.Column(db.String(1000), nullable=False)
    dateposted = db.Column(db.DateTime, nullable= False, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"{self.id} - {self.blogtitle}"

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

class NewpostForm(FlaskForm):
    blogtitle = StringField('Blog Title', validators=[DataRequired()])
    blogcontent = TextAreaField('Blog Content', validators=[DataRequired()])
    submit = SubmitField('Submit' )

@app.route('/')
def homeh():
    return redirect(url_for('home'))

@app.route('/home')
def home():
    allblog = blogpost.query.all()
    return render_template("home.html",  title="Home", allblog=allblog)

@app.route('/about')
def about():
    return render_template("about.html", title="About")

@app.route('/blogs')
def blogs():
    allblog = blogpost.query.all()
    return render_template("blogs.html", title="Blogs", allblog=allblog)

@app.route('/blogs/<id>',  methods=['GET', 'POST'])
def showblog(id):
    blog = blogpost.query.get_or_404(id)
    return render_template("showblog.html",title= blog.blogtitle, blog = blog)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form= LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            if form.email.data == 'admin@blog.com' and form.password.data == 'password':
                flash('You have been logged in!', 'success')
                return redirect(url_for('home'))
            else:
                flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template("login.html", title="Log In", form=form, name=session.get('blogtitle'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form= SignupForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            flash(f'Account created for {form.username.data}!', 'success')
            return redirect(url_for('login'))
    return render_template("signup.html", title="Sign Up", form=form)

@app.route('/create', methods=['GET', 'POST'])
def create():
    form= Create()
    if request.method == 'POST':
        if form.validate_on_submit:
            blogtitle = form.blogtitle.data
            blogcontent = form.blogcontent.data
            blog = blogpost(blogtitle= blogtitle, blogcontent= blogcontent)
            db.session.add(blog)
            db.session.commit()
            flash("Posted a new Blog successfully!")
            return redirect(url_for('home'))
    return render_template('create.html', title="New Post", form=form, name=session.get('blogtitle'))
    


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', title="Error 404"), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html', title="Error 500"), 500   

if __name__ == '__main__':  
    app.run(debug=True) 

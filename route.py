from flask import Flask, render_template, flash, redirect, session, url_for, request
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, PasswordField
from wtforms.validators import DataRequired
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import *
import os

app=Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///blogpost.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SECRET_KEY'] =  os.environ.get('SECRET_KEY')

bootstrap = Bootstrap(app)
db = SQLAlchemy(app)

class blogpost(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    blogtitle = db.Column(db.String(255), nullable=False)
    blogcontent = db.Column(db.String(1000), nullable=False)
    dateposted = db.Column(db.DateTime, nullable= False, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"{self.id} - {self.blogtitle}"

class Login(FlaskForm):
    username = StringField('Blog Title', validators=[DataRequired()])
    password = PasswordField('Blog Title', validators=[DataRequired()])
    login =  SubmitField('Submit' )

class Create(FlaskForm):
    blogtitle = StringField('Blog Title', validators=[DataRequired()])
    blogcontent = TextAreaField('Blog Content', validators=[DataRequired()])
    submit = SubmitField('Submit' )

@app.route('/', methods=['GET', 'POST'])
def log():
    loginform= Login()
    if request.method == 'POST':
        if loginform.validate_on_submit:
            flash("Successfully logged in!")
            return redirect(url_for('home'))
        else:
            flash("Successfully logged in!")
            return redirect(url_for('log'))   
    return render_template("login.html",form=loginform, name=session.get('blogtitle'))

@app.route('/home')
def home():
    allblog = blogpost.query.all()
    return render_template("home.html",  allblog=allblog)

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
    return render_template('create.html', form=form, name=session.get('blogtitle'))
    
@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/blogs')
def blogs():
    allblog = blogpost.query.all()
    return render_template("blogs.html", allblog=allblog)

@app.route('/blogs/<id>',  methods=['GET', 'POST'])
def showblog(id):
    blog = blogpost.query.filter(blogpost.id == id)
    return render_template("showblog.html",blog = blog)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500   

if __name__ == '__main__':  
    app.run()
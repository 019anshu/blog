from flask import Flask, render_template, flash, redirect, session, url_for, request
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired
from wtforms.fields.html5 import EmailField

app=Flask(__name__)

app.config['SECRET_KEY'] = 'any secret string'

bootstrap = Bootstrap(app)

class Create(FlaskForm):
    blogtitle = StringField('Blog Title', validators=[DataRequired()])
    blogcontent = TextAreaField('Blog Content', validators=[DataRequired()])
    submit = SubmitField('Submit' )

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/create', methods=['GET', 'POST'])
def create():
    form= Create()
    if request.method == 'POST':
        if form.validate_on_submit:
            blogtitle = form.blogtitle.data
            blogcontent = form.blogcontent.data
            return redirect(url_for('create'))

    return render_template('create.html', form=form, name=session.get('blogtitle'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500   

if __name__ == '__main__':  
    app.run()
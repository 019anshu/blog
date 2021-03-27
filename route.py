from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm

app=Flask(__name__)
bootstrap = Bootstrap(app)



@app.route('/')
def home():
    return render_template("home.html")

@app.route('/create', methods=['GET', 'POST'])
def create():
    
    return render_template("create.html")

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500   

if __name__ == '__main__':  
    app.run()
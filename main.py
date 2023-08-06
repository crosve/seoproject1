from flask import Flask, render_template, redirect, url_for, flash, request
from forms import RegistrationForm, LoginForm
from flask_behind_proxy import FlaskBehindProxy
from flask_sqlalchemy import SQLAlchemy
from RecipeSearch import recipesearch
import requests
import git
import os


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)



@app.route('/')
def index():
    
    
    return render_template("homepage.html", title="hey")

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(f'account created for {form.username.data}!', 'Success')
        return redirect(url_for('index'))
    return render_template('register.html', form=form)

@app.route('/about')
def aboutpage():
    return render_template('about.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        name = form.username.data
        email = form.email.data
        password= form.password.data
        datatable = User.query.all()
        for data in datatable:
            if data.username == name and data.email == email and data.password == password:
                form = recipesearch()
                return redirect('/login/recipes')
        flash(f'Account not found for {name}, please create an account')
        


    return render_template('login.html', form=form)

@app.route('/login/recipes', methods=['GET', 'POST'])
def recipes():

    form = recipesearch()
    if form.validate_on_submit():
        name = form.recipename.data
        api_url = 'https://api.api-ninjas.com/v1/recipe?query={}'.format(name)
        response = requests.get(api_url, headers={'X-Api-Key': 'pRSxoIYzO8my7bnUgVOvEA==UP7wKGvHesLLxb5S'})
        if response.status_code == requests.codes.ok:
            data = response.json()
            print(data)
            return render_template('recipesearch.html', form = form, data = data)
            
        else:
            print("Error:", response.status_code, response.text)

        


    return render_template('recipesearch.html', form=form)

@app.route("/update_server", methods=['POST'])
def webhook():
    if request.method == 'POST':
        repo = git.Repo('/home/crosve/seoproject1')
        origin = repo.remotes.origin
        origin.pull()
        return 'Updated PythonAnywhere successfully', 200
    else:
        return 'Wrong event type', 400


#maps user attributes to table columns 
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"
    
#creates the tables 
with app.app_context():
    db.create_all()

SECRET_KEY = os.urandom(32)
if __name__ == '__main__':
    app.config['SECRET_KEY'] = SECRET_KEY
    app.run(host="0.0.0.0", port=80)
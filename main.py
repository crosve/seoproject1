from flask import Flask, render_template, redirect, url_for, flash, request, session
from forms import RegistrationForm, LoginForm, inputRecipe
from flask_behind_proxy import FlaskBehindProxy
from flask_sqlalchemy import SQLAlchemy
from RecipeSearch import recipesearch
from flask_wtf.csrf import CSRFProtect
import requests
import git
import os
from flask_session import Session


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_BINDS'] ={
    'SavedRecipes' : 'sqlite:///rip.db'
}
db = SQLAlchemy(app)
csrf = CSRFProtect(app)

SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['WTF_CSRF_SECRET_KEY'] = "secretkey"
csrf.init_app(app)

#to save the current user who's logged in 
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route('/')
def index():
    
    
    return render_template("homepage.html", title="hey")

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegistrationForm()
    if form.validate_on_submit():
        userName = form.username.data
        Email = form.email.data
        datatable = User.query.all()
        #check if user or email already exist in our data base
        for data in datatable:
            if data.username == userName or data.email == Email:
                flash(f'Account already created for {userName}. Please login')
                return render_template('register.html', form=form)
        user = User(username=form.username.data, email=form.email.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.username.data}!')
        return render_template('register.html', form=form)
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
                    
                session["name"] = name
                
                return redirect('/login/recipes')
        flash(f'Account not found for {name}, please create an account')
        
        
    elif "name" in session:
        return redirect('/login/recipes')
    
    return render_template('login.html', form=form)

@app.route('/login/recipes', methods=['GET', 'POST'])
def recipes():
    if "name" in session:
        user = session["name"]
        form = recipesearch()
        recipeform = inputRecipe()
        if form.validate_on_submit():
            name = form.recipename.data
            api_url = 'https://api.api-ninjas.com/v1/recipe?query={}'.format(name)
            response = requests.get(api_url, headers={'X-Api-Key': 'pRSxoIYzO8my7bnUgVOvEA==UP7wKGvHesLLxb5S'})
            if response.status_code == requests.codes.ok:
                data = response.json()
                
                return render_template('recipesearch.html', form = form, data = data, user=user, name=name,  recipeform=recipeform)
                
            else:
                print("Error:", response.status_code, response.text, user=user)
        if recipeform.validate_on_submit():
            rName = recipeform.recipeName.data
            
            newrecipes = Recipes(recipename=rName, owner = user)
            db.session.add(newrecipes)
            db.session.commit()


        return render_template('recipesearch.html', form=form, user=user, recipeform= recipeform)
    
    else:
        return redirect("/login")
    
@app.route('/test', methods=['GET', 'POST'])
def test():
    newform = inputRecipe()
   

    return render_template('saved.html', newform=newform)

@app.route('/logout')
def logout():
    session.pop('name', None)
    return redirect('/login')

@app.route('/saved', methods=['GET', 'POST'])
def saved():
    if "name" in session:
        user = session["name"]
        datatable = Recipes.query.all()
        personalrecipes = []
        # personalrecipes.append('cake')
        # personalrecipes.append('coffee')
        for data in datatable:
            if data.owner == user:
                personalrecipes.append(data.recipename)
        

        return render_template('saved.html', user=user, personalrecipes=personalrecipes)
    
    else:
        return redirect('/login')

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
    
class Recipes(db.Model):
    __bind_key__ = "SavedRecipes"
    id = db.Column(db.Integer, primary_key=True)
    owner = db.Column(db.String(20), unique=False, nullable=False)

    recipename = db.Column(db.String(120), unique=False, nullable=False)

    
    def __repr__(self):
        return f"User('{self.owner}', '{self.recipename}')"


#creates the tables 
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    # SECRET_KEY = os.urandom(32)
    # app.config['SECRET_KEY'] = SECRET_KEY
    app.run(host="0.0.0.0", port=80)
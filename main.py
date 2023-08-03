from flask import Flask, render_template, redirect, url_for, flash, request
from forms import RegistrationForm
from flask_behind_proxy import FlaskBehindProxy
from flask_sqlalchemy import SQLAlchemy



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

@app.route('/login')
def login():


    

    return render_template('login.html')


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


if __name__ == '__main__':
    app.config['SECRET_KEY'] = '2a174b7c4f47cf4fdb504ff4f5f6d772'
    app.run(host="0.0.0.0", port=80)
from datetime import datetime
from flask import Flask, request, render_template, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
import bcrypt

app = Flask(__name__)

# Update MySQL database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:123456@localhost/student'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'secret_key'

db = SQLAlchemy(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

    def __init__(self, email, password, name):
        self.name = name
        self.email = email
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))

# Driver model
class Driver(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))

# Create all tables in the database
with app.app_context():
    db.create_all()

# Info model
class Info(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(100), nullable=False)
    Phone = db.Column(db.String(100), nullable=False)
    Place = db.Column(db.String(100), nullable=False)
    Time = db.Column(db.String(100), nullable=False)

with app.app_context():
    db.create_all()

# Present model
class Present(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(100), nullable=False)
    Date = db.Column(db.String(100), nullable=False)
    Present = db.Column(db.String(100), nullable=False)

with app.app_context():
    db.create_all()

# Home model
class Home(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(100), nullable=False)
    Time = db.Column(db.String(100), nullable=False)
    Date = db.Column(db.String(100), nullable=False)

with app.app_context():
    db.create_all()

@app.route('/index')
def index():
    return render_template('index.html')
@app.route('/')
def home():
    return render_template('home.html')
@app.route('/DriverLogin', methods=['POST'])
def DriverLogin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['pswd']

        user = Driver.query.filter_by(email=email).first()

        if user and user.check_password(password):
            session['email'] = user.email
            return redirect('driver_dashboard')
        else:
            return render_template('DriverLogin.html', error='Invalid user')

    return render_template('DriverLogin.html')


@app.route('/DriverRegister', methods=['POST'])
def Driverregister():
    if request.method == 'POST':
        name = request.form['username']
        email = request.form['email']
        password = request.form['pswd']

        existing_user = Driver.query.filter_by(email=email).first()
        if existing_user:
            return render_template('DriverLogin.html', error='User with this email already exists.')

        new_user = User(name=name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect('DriverLogin')

    return render_template('DriverLogin.html')


@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['pswd']

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            session['email'] = user.email
            return redirect('/dashboard')
        else:
            return render_template('index.html', error='Invalid user')

    return render_template('index.html')


@app.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        name = request.form['username']
        email = request.form['email']
        password = request.form['pswd']

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return render_template('index.html', error='User with this email already exists.')

        new_user = User(name=name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect('/index')

    return render_template('index.html')


@app.route('/driver_dashboard')
def driver_dashboard():
    if 'driver_email' not in session:
        return redirect('/driver_login')

    driver = Driver.query.filter_by(email=session['driver_email']).first()
    return render_template('/static/dashboard.html', driver=driver)

@app.route('/dashboard')
def dashboard():
    if 'email' in session:
        user = User.query.filter_by(email=session['email']).first()
        return render_template('dashboard.html', user=user)

    return redirect('registration.html')

@app.route('/registeration', methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        name = request.form['Name']
        phone = request.form['Phone']
        place = request.form['Place']
        time = request.form['Time']

        new_info = Info(Name=name, Phone=phone, Place=place, Time=time)
        db.session.add(new_info)
        db.session.commit()

        return "success"

    return render_template('registration.html')

@app.route('/prebook', methods=['GET', 'POST'])
def prebook():
    if request.method == 'POST':
        name = request.form['Name']
        date_str = request.form['Date']
        present = request.form['Present']

        date_obj = datetime.strptime(date_str, '%d/%m/%Y').date()
        new_present = Present(Name=name, Date=date_obj, Present=present)
        db.session.add(new_present)
        db.session.commit()

        return "success"

    return render_template('prebook.html')

@app.route('/departure', methods=['GET', 'POST'])
def departure():
    if request.method == 'POST':
        name = request.form['Name']
        time = request.form['Time']
        date_str = request.form['Date']

        date_obj = datetime.strptime(date_str, '%d/%m/%Y').date()

        new_home = Home(Name=name, Time=time, Date=date_obj)
        db.session.add(new_home)
        db.session.commit()

        return redirect('/departure')

    home_data = Home.query.order_by(Home.Date.desc(), Home.Time.asc()).all()

    return render_template('departure.html', home_data=home_data)

@app.route('/driver')
def driver():
    return render_template('driver.html')

@app.route('/logoutt')
def logoutt():
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)

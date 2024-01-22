from flask import Flask, render_template, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, Text
from sqlalchemy_utils import database_exists, create_database
from datetime import datetime
from flask_migrate import Migrate
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from werkzeug.security import generate_password_hash, check_password_hash





app = Flask(__name__)
app.config['DEBUG'] = True
#Add secret key for forms generated with python code and not in html
app.config['SECRET_KEY'] = "my secret key"
#Add Database
password = 'mysqlrootpw'
database_uri = 'mysql+pymysql://root:'+ password +'@localhost/school-system'
app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
#Create the database if not exist
FirstTimeConnectionToDatabase = False
engine = create_engine(database_uri)
if not database_exists(engine.url):
    create_database(engine.url)
    print('Database created')
    FirstTimeConnectionToDatabase = True
#Initialize The Database
db = SQLAlchemy(app)
migrate = Migrate(app, db)
#Database models scroll to bottom
#Form classes
class RegUserForm(FlaskForm):
    username = StringField("Please enter a Username", validators=[DataRequired()])
    hashed_password = PasswordField('Password', validators=[DataRequired(), EqualTo("hashed_password2", message='Passwords must match')])
    hashed_password2 = PasswordField('Confirm Password', validators=[DataRequired()])
    register = SubmitField("Register")

@app.route('/')
def loadLogin():
    return render_template("index.html")

@app.route('/mainpage.html')
def loadmain():
    #retrieve user data from db and put username on the mainpage
    return render_template("mainpage.html")

@app.route('/sinfo.html')
def loadSInfoPage():
    return render_template("sinfo.html")

@app.route('/scoreentry.html')
def loadScoreEntryPage():
    return render_template("scoreentry.html")

@app.route('/subject.html')
def loadSubjectPage():
    return render_template("subject.html")

@app.route('/statistics.html')
def loadStatisticsPage():
    return render_template("statistics.html")

@app.route('/reportgen.html')
def loadGenReportPage():
    return render_template("reportgen.html")

@app.route('/add_user.html', methods=['GET', 'POST'])
def add_user():
    form = RegUserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user is None:
            hashed_pw = generate_password_hash(form.hashed_password.data)
            user = Users(username=form.username.data, hashed_password=hashed_pw)
            db.session.add(user)
            db.session.commit()
        form.username.data = ''
        form.hashed_password.data=''
        form.hashed_password2.data=''
        flash("User added")
    our_users = Users.query.order_by(Users.date_added)
    return render_template('add_user.html', form = form, our_users = our_users)

if __name__ == '__main__':
    app.run(port=5000)

#Database models
#Users table
class Users(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(64), nullable = False, unique = True)
    hashed_password = db.Column(db.String(200), nullable = False) #need to add hashpw later
    date_added = db.Column(db.DateTime, default = datetime.utcnow)

    @property
    def password(self):
        raise AttributeError('password is not readable attribute')

    @password.setter
    def password(self, password):
        self.hashed_password = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.hashed_password, password)

    def __repr__(self): return '<Name %r>' % self.username

#Subjects table
class Subjects(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    remarks = db.relationship('Remarks', backref='subject', lazy=True)
    assessments = db.relationship('Assessments', backref='subject', lazy=True)

class Remarks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    content = db.Column(db.String(100), nullable=False)
    assessments = db.relationship('Assessments', backref='remark',lazy=True)

class Assessments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    remark_id = db.Column(db.Integer, db.ForeignKey('remarks.id'), nullable=False)
    full_mark = db.Column(db.Integer, nullable=False, default=100)
    percentage_to_remark = db.Column(db.Float, nullable=False, default=100)

#Student Info tables
class Classes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    students = db.relationship('Students', backref='class', lazy=True)

class Students(db.Model):
    sid = db.Column(db.String(100), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    student_class = db.Column(db.Integer, db.ForeignKey('classes.id'))
    dob = db.Column(db.DateTime)
    absentdays = db.Column(db.Integer, default=0)
    latedays = db.Column(db.Integer, default=0)
    teachercomment = db.Column(Text)

#grade tables
class Grade_assessment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sid = db.Column(db.String(100), db.ForeignKey('students.sid') , nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessments.id'), nullable=False)
    grade = db.Column(db.Float)
    transformedgrade = db.Column(db.Float)

class Grade_remark(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sid = db.Column(db.String(100), db.ForeignKey('students.sid'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    remark_id = db.Column(db.Integer, db.ForeignKey('remarks.id'), nullable=False)
    grade = db.Column(db.Float)

#if True:
    #db.create_all()
if FirstTimeConnectionToDatabase:
    db.create_all()
from flask import Flask, render_template, flash, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, Text
from sqlalchemy_utils import database_exists, create_database
from datetime import datetime
from flask_migrate import Migrate
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user





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
#Login stuff
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'loadLogin'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

#Form classes
class RegUserForm(FlaskForm):
    username = StringField("Please enter a Username", validators=[DataRequired()])
    hashed_password = PasswordField('Password', validators=[DataRequired(), EqualTo("hashed_password2", message='Passwords must match')])
    hashed_password2 = PasswordField('Confirm Password', validators=[DataRequired()])
    register = SubmitField("Register")

class updateUserForm(FlaskForm):
    username = StringField("Please enter Username", validators=[DataRequired()])
    hashed_password = PasswordField('Password', validators=[DataRequired(), EqualTo("hashed_password2", message='Passwords must match')])
    hashed_password2 = PasswordField('Confirm Password', validators=[DataRequired()])
    update = SubmitField("Update")

@app.route('/', methods=['GET', 'POST'])
def loadLogin():
    username = ''
    password = ''
    if request.method == "POST":
        username = request.form['UN']
        password = request.form['password']
        user=Users.query.filter_by(username=username).first()
        if user:
            if check_password_hash(user.hashed_password, password):
                login_user(user)
                return redirect(url_for('loadmain'))
            else:
                flash("Wrong Password")
        else:
            flash("User don't exist")
    return render_template("index.html")

@app.route('/logout', methods=["GET","POST"])
@login_required
def logout():
    logout_user()
    flash("Logged out")
    return redirect(url_for('loadLogin'))

@app.route('/mainpage.html')
@login_required
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
@login_required
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

@app.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def UpdateUser(id):
    form=updateUserForm()
    NameToUpdate = Users.query.get_or_404(id)
    our_users = Users.query.order_by(Users.date_added)
    if request.method == "POST":
        NameToUpdate.username = request.form['username']
        NameToUpdate.hashed_password = generate_password_hash(request.form['hashed_password'])
        try:
            db.session.commit()
            flash("User updated")
            return render_template("update.html", form = form, NameToUpdate = NameToUpdate, our_users = our_users)
        except:
            flash("Error, user is not updated")
            return render_template("update.html", form = form, NameToUpdate = NameToUpdate, our_users = our_users)
    else:
        return render_template("update.html", form = form, NameToUpdate = NameToUpdate, our_users = our_users)


@app.route('/delete/<int:id>')
@login_required
def delete(id):
    form = RegUserForm()
    UserToDelete = Users.query.get_or_404(id)
    try:
        db.session.delete(UserToDelete)
        db.session.commit()
        flash("User deleted")
        our_users = Users.query.order_by(Users.date_added)
        return render_template('add_user.html', form = form, our_users = our_users)
    except:
        flash("Error in deleting")
        return render_template('add_user.html', form = form, our_users = our_users)


if __name__ == '__main__':
    app.run(port=5000)

#Database models
#Users table
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(64), nullable = False, unique = True)
    hashed_password = db.Column(db.String(200), nullable = False) 
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
    remarks = db.relationship('Remarks', backref='subject', cascade='all, delete', lazy=True)
    assessments = db.relationship('Assessments', backref='subject', cascade='all, delete', lazy=True)

class Remarks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id', ondelete='CASCADE'), nullable=False)
    content = db.Column(db.String(100), nullable=False)
    assessments = db.relationship('Assessments', backref='remark', cascade='all, delete', lazy=True)

class Assessments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id', ondelete='CASCADE'), nullable=False)
    remark_id = db.Column(db.Integer, db.ForeignKey('remarks.id', ondelete='CASCADE'), nullable=False)
    full_mark = db.Column(db.Integer, nullable=False, default=100)
    percentage_to_remark = db.Column(db.Float, nullable=False, default=100)
    assessment_type = db.Column(db.String(100), nullable=False)

#Student Info tables
class Classes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    students = db.relationship('Students', backref='class', cascade='all, delete', lazy=True)

class Students(db.Model):
    sid = db.Column(db.String(100), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    student_class = db.Column(db.Integer, db.ForeignKey('classes.id', ondelete='CASCADE'), nullable=False)
    dob = db.Column(db.DateTime)
    absentdays = db.Column(db.Integer, default=0)
    latedays = db.Column(db.Integer, default=0)
    teachercomment = db.Column(Text)
    grade_a = db.relationship('Grade_assessment', backref='student', cascade='all, delete', lazy=True)
    grade_r = db.relationship('Grade_remark', backref='student', cascade='all, delete', lazy=True)
    
#grade tables
class Grade_assessment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sid = db.Column(db.String(100), db.ForeignKey('students.sid', ondelete='CASCADE') , nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id', ondelete='CASCADE'), nullable=False)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessments.id', ondelete='CASCADE'), nullable=False)
    grade = db.Column(db.Float)
    transformedgrade = db.Column(db.Float)

class Grade_remark(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sid = db.Column(db.String(100), db.ForeignKey('students.sid', ondelete='CASCADE'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id', ondelete='CASCADE'), nullable=False)
    remark_id = db.Column(db.Integer, db.ForeignKey('remarks.id', ondelete='CASCADE'), nullable=False)
    grade = db.Column(db.Float)

#if True: #This line is for testing purposes
if FirstTimeConnectionToDatabase:
    db.create_all()
    Users(username='admin', hashed_password=generate_password_hash(password))
    db.session.commit()
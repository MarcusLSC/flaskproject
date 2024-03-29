from flask import Flask, render_template, flash, request, redirect, url_for, session
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

def get_SubjectChoices_from_database():
    subjects = Subjects.query.all()
    choices = [(subject.id, subject.name) for subject in subjects]
    choices.insert(0, ('new', 'Create a New Subject'))
    return choices

class SelectSubjectForm(FlaskForm):
    SubjectSelect = SelectField('Select a Subject: ', default='')
    
    def update_choices(self):
        self.SubjectSelect.choices = get_SubjectChoices_from_database()

class SubjectForm(FlaskForm):
        SubjectName = StringField("Subject Name: ", validators=[DataRequired()])

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

@app.route('/subject.html', methods=["GET","POST"])
def loadSubjectPage():
    form1 = SelectSubjectForm()
    subjects = Subjects.query.all()
    choices = [(subject.id, subject.name) for subject in subjects]
    form1.update_choices()
    form2 = SubjectForm()
    RequiredSubject = None
    form2.SubjectName.data=''
    previous_value = session.get('previous_value')
    form1.SubjectSelect.data=previous_value
    if form1.validate_on_submit():
        if request.method == "POST":
            form_identifier = request.form.get("form_identifier")

            if form_identifier == "form1":
                selected_subject = form1.SubjectSelect.data
                session['previous_value'] = selected_subject
                
                if selected_subject != 'new':
                    form1.SubjectSelect.data=selected_subject
                    RequiredSubject = Subjects.query.filter_by(id=selected_subject).first()
                    InfoforRemark = Remarks.query.filter_by(subject_id=RequiredSubject.id).order_by(Remarks.id)
                    InfoforAssessment = Assessments.query.filter_by(subject_id=RequiredSubject.id).order_by(Assessments.id)
                    form2.SubjectName.data=RequiredSubject.name
                    return render_template("asubject.html",form1=form1,form2=form2, remarks=InfoforRemark, assessments=InfoforAssessment, name=RequiredSubject.name)

            if form_identifier =="form2":
                if previous_value == 'new':
                    # Handle the case where the user wants to create a new subject
                    # Redirect to a form for creating a new subject
                    if form2.validate_on_submit():
                        NewSubjectName=form2.SubjectName.data
                        NewSubject = Subjects(name=NewSubjectName)
                        try:
                            db.session.add(NewSubject)
                            db.session.flush()
                            remarks = request.form.getlist('remarks[]')
                            for remark in remarks:
                                NewRemark=Remarks(subject_id=NewSubject.id, content=remark)
                                try:
                                            db.session.add(NewRemark)
                                            db.session.flush()    
                                except:
                                            flash("Error, remarks is not saved")
                                            print("Error, remarks is not saved")
                                            return render_template("subject.html",form1=form1,form2=form2,choices = choices)
                                ReqRemarks=Remarks.query.filter_by(name=NewSubjectName).order_by(remark.id)
                                assignments_names = request.form.getlist('assignmentName[]')
                                assignment_relations = request.form.getlist('assignmentRelationWithRemark[]')
                                assignment_full_marks = request.form.getlist('assignmentFullMark[]')
                                assignment_contributions = request.form.getlist('assignmentContribution[]')
                                if assignments_names != None:
                                    for ReqRemark in ReqRemarks:
                                        for name, relation, full_mark, contribution in zip(assignments_names, assignment_relations, assignment_full_marks, assignment_contributions):
                                            if ReqRemark.content == relation:
                                                NewAssessment = Assessments(name=name, subject_id=NewSubject.id, remark_id=ReqRemark.id, full_mark=full_mark, percentage_to_remark=contribution, assessment_type="assignment")
                                                try:
                                                        db.session.add(NewAssessment)
                                                        db.session.flush()    
                                                except:
                                                        flash("Error, assignment is not saved")
                                                        print("Error, assignment is not saved")
                                                        return render_template("subject.html",form1=form1,form2=form2,choices = choices)
                                    quiz_names = request.form.getlist('quizName[]')
                                    quiz_relations = request.form.getlist('quizRelationWithRemark[]')
                                    quiz_full_marks = request.form.getlist('quizFullMark[]')
                                    quiz_contributions = request.form.getlist('quizContribution[]')
                                    if quiz_names !=None:
                                        for ReqRemark in ReqRemarks:
                                            for name, relation, full_mark, contribution in zip(quiz_names, quiz_relations, quiz_full_marks, quiz_contributions):
                                                if ReqRemark.content == relation:
                                                    NewAssessment = Assessments(name=name, subject_id=NewSubject.id, remark_id=ReqRemark.id, full_mark=full_mark, percentage_to_remark=contribution, assessment_type="quiz")
                                                    try:
                                                        db.session.add(NewAssessment)
                                                        db.session.flush()    
                                                    except:
                                                        flash("Error, quiz is not saved")
                                                        print("Error, quiz is not saved")
                                                    return render_template("subject.html",form1=form1,form2=form2)            
                                    examination_names = request.form.getlist('examinationName[]')
                                    examination_relations = request.form.getlist('examinationRelationWithRemark[]')
                                    examination_full_marks = request.form.getlist('examinationFullMark[]')
                                    examination_contributions = request.form.getlist('examinationContribution[]')
                                    if examination_names!=None:
                                        for ReqRemark in ReqRemarks:
                                            for name, relation, full_mark, contribution in zip(examination_names, examination_relations, examination_full_marks, examination_contributions):
                                                if ReqRemark.content == relation:
                                                    NewAssessment = Assessments(name=name, subject_id=NewSubject.id, remark_id=ReqRemark.id, full_mark=full_mark, percentage_to_remark=contribution, assessment_type="exam")
                                                    try:
                                                        db.session.add(NewAssessment)
                                                        db.session.flush()    
                                                    except:
                                                        flash("Error, exam is not saved")
                                                        print('Error, exam is not saved')
                                                        return render_template("subject.html",form1=form1,form2=form2,choices = choices)
                                    other_names = request.form.getlist('otherName[]')
                                    other_relations = request.form.getlist('otherRelationWithRemark[]')
                                    other_full_marks = request.form.getlist('otherFullMark[]')
                                    other_contributions = request.form.getlist('otherContribution[]')
                                    if other_names != None:
                                        for ReqRemark in ReqRemarks:
                                            for name, relation, full_mark, contribution in zip(other_names, other_relations, other_full_marks, other_contributions):
                                                if ReqRemark.content == relation:
                                                    NewAssessment = Assessments(name=name, subject_id=NewSubject.id, remark_id=ReqRemark.id, full_mark=full_mark, percentage_to_remark=contribution, assessment_type="other")
                                                    try:
                                                        db.session.add(NewAssessment)
                                                        db.session.flush()    
                                                    except:
                                                        flash("Error, others item is not saved")
                                                        print("Error, others item is not saved")
                                                        return render_template("subject.html",form1=form1,form2=form2,choices = choices)
                                    db.session.commit()
                                    flash("Subject added successfully")
                                    print("Subject added successfully")
                        except:
                                flash("Error, subject is not saved")
                                print("Error, subject is not saved")
                                return render_template("subject.html",form1=form1,form2=form2,choices = choices)
                        form1.update_choices()                
                        return render_template("subject.html",form1=form1,form2=form2,choices = choices)
    return render_template("subject.html",form1=form1,form2=form2,choices = choices)    
    

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
    name = db.Column(db.String(100), nullable=False)
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
    sid = db.Column(db.String(100), primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id', ondelete='CASCADE'), nullable=False)
    assessment_id = db.Column(db.Integer, primary_key=True)
    grade = db.Column(db.Float)
    transformedgrade = db.Column(db.Float)
    __table_args__ = (
        db.ForeignKeyConstraint(['sid'], ['students.sid'], ondelete='CASCADE'),
        db.ForeignKeyConstraint(['assessment_id'], ['assessments.id'], ondelete='CASCADE')
    )

class Grade_remark(db.Model):
    sid = db.Column(db.String(100), primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id', ondelete='CASCADE'), nullable=False)
    remark_id = db.Column(db.Integer, primary_key=True)
    grade = db.Column(db.Float)
    __table_args__ = (
        db.ForeignKeyConstraint(['sid'], ['students.sid'], ondelete='CASCADE'),
        db.ForeignKeyConstraint(['remark_id'], ['remarks.id'], ondelete='CASCADE')
    )

#if True: #This line is for testing purposes
if FirstTimeConnectionToDatabase:
    db.create_all()
    Users(username='admin', hashed_password=generate_password_hash(password))
    db.session.commit() #Current test acc: username=test, pw=password
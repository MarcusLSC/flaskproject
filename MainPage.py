from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from datetime import datetime
#from flask_migrate import Migrate





app = Flask(__name__)
#Add secret key for forms generated with python code and not in html
app.config['SECRET_KEY'] = "my secret key"
#Add Database
password = ''
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
#migrate = Migrate(app, db)

#Database models scroll to bottom

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

if __name__ == '__main__':
    app.run(port=5000)

#Database models
#Users table
#class Users(db.Model):
 #   id = db.Column(db.Integer, primary_key = True)
  #  username = db.Column(db.String(64), nullable = False, unique = True)
  #  hashed_password = db.Column(db.String(200), nullable = False) #need to add hashpw later
   # date_added = db.Column(db.DateTime, default = datetime.utcnow)

    #def __repr__(self): return '<Name %r>' % self.username

#Subjects table
class Subjects(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

class Remarks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'))
    subject = db.relationship('Subjects', backref=db.backref('remarks', lazy=True))
    content = db.Column(db.String(100), nullable=False)

class Assessments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'))
    subject = db.relationship('Subjects', backref=db.backref('assessments', lazy=True))
    remark_id = db.Column(db.Integer, db.ForeignKey('remarks.id'))
    remark = db.relationship('Remarks', backref=db.backref('assessments', lazy=True))
    percentage_to_remark = db.Column(db.Float)
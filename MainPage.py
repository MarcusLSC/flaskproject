from flask import Flask, render_template
app = Flask(__name__)
@app.route('/')
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
def loadGenReportPage():
    return render_template("statistics.html")

if __name__ == '__main__':
    app.run(port=5000)
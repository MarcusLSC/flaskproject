from flask import Flask, render_template
StudentInfoPage = Flask(__name__)
@StudentInfoPage.route('/')

def loadSInfoPage ():
    return render_template("sinfo.html")


if __name__ == '__main__':
    loadSInfoPage.run(port = 5002)
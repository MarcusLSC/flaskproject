from flask import Flask, render_template
MainPage = Flask(__name__)
@MainPage.route('/')

def loadmain():
    #retrieve user data from db and put username on the mainpage
    return render_template("mainpage.html")

if __name__ == '__main__':
    MainPage.run(port=5001)
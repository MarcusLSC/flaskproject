from flask import Flask, render_template
LoginPage = Flask(__name__)
@LoginPage.route('/')
def loadLogin():
    return render_template("index.html")
# add functions for login and cookies for session

if __name__ == '__main__':
    LoginPage.run(port = 5000)
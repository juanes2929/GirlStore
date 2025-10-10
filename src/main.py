
from service.connection import ConnectionDB
import flask_cors
from flask import Flask, request, redirect, render_template, url_for, session, flash, jsonify




app = Flask(__name__)
app.secret_key = "GirlStore"
flask_cors.CORS(app)

@app.errorhandler(404)
def PaginaNoEncontrada(error):
    return redirect("/home")

@app.route("/")
def tologin():
    return redirect("/home")

@app.route("/login")
def login():
    pass

@app.route("/home")
def home():
    return render_template("home.html")


if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0',port=9000)
from flask import Flask, render_template, url_for, request, redirect
from argon2 import PasswordHasher, exceptions

roleOptions = ['Student', 'Teacher']

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register')
def register():
    return(render_template('register.html', roleOptions = roleOptions))

@app.route('/request')
def handle_request(methods = 'POST'):
    #TODO: Make async request
    if(request.form.get('role') in roleOptions):
        
        pwHasher = PasswordHasher()

        fname = request.form.get('fname')
        lname = request.form.get('lname')
        email = request.form.get('email')
        pw = request.form.get('password')
        role = request.form.get('role')

        pw = pw.encode()
        hashedPW = pwHasher.hash(pw)



    else:
        return(redirect('/register'))


if __name__ == "__main__":
    app.run(debug = True)
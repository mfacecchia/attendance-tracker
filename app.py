from flask import Flask, render_template, url_for, request, redirect
from argon2 import PasswordHasher, exceptions
import mysql.connector

app = Flask(__name__)

#List of roles available for the registration
roleOptions = ['Studente', 'Insegnante']
#Creating a variable used to store all available courses from the database and pass them to the HTML template
courses = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register')
def register():

    connection = connectToDB()
    cursor = connection.cursor()
    cursor.execute("select nomeCorso from Corso")

    global courses
    #Clearing courses list in order to correctly store all available courses
    courses = []
    for course in cursor:
        #Getting the first element of each row
        courses.append(course[0])
    return(render_template('register.html', roleOptions = roleOptions, courses = courses))

@app.route('/register/request', methods = ['POST'])
def handle_request():
    #TODO: Make async request
    if(request.form.get('role') in roleOptions and request.form.get('course') in courses):
        
        pwHasher = PasswordHasher()

        fname = request.form.get('fname')
        lname = request.form.get('lname')
        email = request.form.get('email')
        pw = request.form.get('password')
        role = request.form.get('role')
        course = request.form.get('course')

        pw = pw.encode()
        hashedPW = pwHasher.hash(pw)

        connection = connectToDB()
        if(not connection):
            return "<h1>Connection error</h1>"
        #Creating a cursor reponsible for query executions
        cursor = connection.cursor()

        #Add unique field check
        cursor.execute('insert into Utente values(%(email)s, %(name)s, %(surname)s, %(pw)s, %(role)s, %(course)s)', {'email': email, 'name': fname, 'surname': lname, 'pw': hashedPW, 'role': role, 'course': course})
        #Sending request to DB
        connection.commit()
        #Closing connection
        cursor.close()
        connection.close()
        return "<h1>Success!</h1>"
    else:
        #Redirecting back to register page if the input values are not correct
        return(redirect('/register'))


def connectToDB():
    '''Starts a connection to the database with the given data'''
    try:
        connection = mysql.connector.connect(user = 'root', password = '', host = 'localhost', database = 'Attendance_Tracker')
    except mysql.connector.Error:
        return False
    return connection

if __name__ == "__main__":
    app.run(debug = True)
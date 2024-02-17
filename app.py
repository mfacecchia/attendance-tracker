from flask import Flask, render_template, url_for, request, redirect, session,flash, Response
from argon2 import PasswordHasher, exceptions
import mysql.connector

app = Flask(__name__)
app.config['SECRET_KEY'] = 'PNfxz1zt41{E2h2T=,#=&Rz4xXv-kE'
app.config['SESSION_TYPE'] = 'filesystem'

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
    #Printing out an error message if the connection to database fails
    if(not connection):
        return "The registration service is having problems... Please try reloading the page or try again later"
    cursor = connection.cursor()
    cursor.execute("select nomeCorso from Corso")

    global courses
    #Clearing courses list in order to correctly store all available courses
    courses = []
    for course in cursor:
        #Getting the first element of each row
        courses.append(course[0])
    return(render_template('register.html', roleOptions = roleOptions, courses = courses))

@app.route('/login')
def login():
    #Redirecting to user screening page if the user is already logged in
    if(session.get('name')):
        return redirect(url_for('userScreening'))
    return(render_template('login.html'))

@app.route('/login/request', methods = ['GET', 'POST'])
def check_login():
    if(request.form.get('email')):
        email = request.form.get('email')
        pw = request.form.get('password')
        
        connection = connectToDB()
        if(not connection):
            return "The registration service is having problems... Please try reloading the page or try again later"
        cursor = connection.cursor()
        #Getting all data from the database related to that single email (representing PRIMARY KEY)
        cursor.execute('select * from Utente where Email = %(email)s', {'email': email})
        
        response = cursor.fetchone()
        #`response == None` means that no user with the input email was found in the database
        if(response == None):
            return "Account not found"
        phasher = PasswordHasher()
        try:
            #Verifying the hashed password gotten from the database with the user input one in the form
            phasher.verify(response[3], pw)
        #Non-matching passwords will throw `VerifyMismatchError`
        #Redirecting to login page form to retry the input
        except exceptions.VerifyMismatchError:
            #Sending an error message to back to the login page in order to display why the login didn't happen
            flash('The password is incorrect. Please try again.', 'error')
        else:
            #Dinamically changing session permanent state based on form checkbox
            if(request.form.get('remember')):
                session.permanent = True
            else:
                session.permanent = False
            #Getting all useful user data and creating all relative session fields
            session['name'] = response[1]
            session['surname'] = response[2]
            session['role'] = response[4]
            session['course'] = response[5]
            return redirect(url_for('userScreening'))
        finally:
            connection.close()
            cursor.close()
    else:
        flash("An error occured while submitting the form. Please try again.", 'error')
    return redirect('/login')

@app.route('/register/request', methods = ['GET', 'POST'])
def handle_request():
    #TODO: Make async request
    if(request.form.get('role') in roleOptions and request.form.get('course') in courses):

        fname = request.form.get('fname')
        lname = request.form.get('lname')
        email = request.form.get('email')
        pw = request.form.get('password')
        role = request.form.get('role')
        course = request.form.get('course')

        pHasher = PasswordHasher()
        pw = pw.encode()
        hashedPW = pHasher.hash(pw)

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
        flash('An error occured while handling your request... Please try again.', 'error')
        return(redirect('/register'))

@app.route('/user')
def userScreening():
    if(session.get('name')):
        return render_template('userScreening.html', session = session)
    else:
        flash('Please login', 'error')
        return redirect(url_for('login'))


def connectToDB():
    '''Starts a connection to the database with the given data'''
    try:
        connection = mysql.connector.connect(user = 'root', password = '', host = 'localhost', database = 'Attendance_Tracker')
    except mysql.connector.Error:
        return False
    return connection

@app.route('/user/logout')
def logout():
    #Checking if session exists before clearing it
    if(session.get('name')):
        session.clear()
        flash("Successfully logged out.", 'success')
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug = True)
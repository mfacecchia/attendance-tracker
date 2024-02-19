from flask import Flask, render_template, url_for, request, redirect, session,flash, Response
from argon2 import PasswordHasher, exceptions
import mysql.connector
from authlib.integrations.flask_client import OAuth

app = Flask(__name__)
oauth = OAuth(app)
app.config['SECRET_KEY'] = 'PNfxz1zt41{E2h2T=,#=&Rz4xXv-kE'
app.config['SESSION_TYPE'] = 'filesystem'

#GITHUB CONFIG DATA
app.config['GITHUB_CLIENT_ID'] = 'e4114fcd0190e9c4132d'
app.config['GITHUB_CLIENT_SECRET'] = '7d141726bbe60d55e0bcb712c505aa6ab4ccde92'
#Registering OAuth application for future requests
oauth.register(
    'github',
    client_id = app.config['GITHUB_CLIENT_ID'],
    client_secret = app.config['GITHUB_CLIENT_SECRET'],
    access_token_url = 'https://github.com/login/oauth/access_token',
    authorize_url = 'https://github.com/login/oauth/authorize',
    api_base_url = 'https://api.github.com/',
    client_kwargs = {'scope': 'user:email'}
)

#List of roles available for the registration
roleOptions = ['Studente', 'Insegnante', 'Admin']
#Creating a variable used to store all available courses from the database and pass them to the HTML template
courses = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/auth/github')
def githubAuth():
    #NOTE: `_external` means that it's pointing to an external domain
    return oauth.github.authorize_redirect(url_for('authorize', _external = True))

@app.route('/github/callback')
def authorize():
    token = oauth.github.authorize_access_token()
    #TODO: Redirect if cancelled authorization
    #TODO: Ask user the role and course for DB
    profile = oauth.github.get('user').json()
    
    connection = connectToDB()
    cursor = connection.cursor()
    #Tries to add data to database, if it raises `IntegrityError`, the data was already input so it skips this step and redirects to the user screening page
    try:
        cursor.execute("insert into Utente(email, nome, TipologiaUtente, NomeCorso) values(%(email)s, %(username)s, %(usertype)s, %(courseName)s)", {'email': profile['id'], 'username': profile['login'], 'usertype': 'Studente', 'courseName': 'Sviluppo Software'})
        connection.commit()
    except mysql.connector.errors.IntegrityError:
        pass
    cursor.close()
    connection.close()
    session['name'] = profile['login']
    session['role'] = 'Studente'
    session['course'] = 'Sviluppo Software'
    return redirect(url_for('userScreening'))

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

@app.route('/user/create', methods = ['GET', 'POST'])
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

        #TODO: Add unique field check
        cursor.execute('insert into Utente(Email, Nome, Cognome, PW, Tipologia, nomeCorso) values(%(email)s, %(name)s, %(surname)s, %(pw)s, %(role)s, %(course)s)', {'email': email, 'name': fname, 'surname': lname, 'pw': hashedPW, 'role': role, 'course': course})
        #Sending request to DB
        connection.commit()
        #Closing connection
        cursor.close()
        connection.close()
        flash('Account created', 'success')
        return redirect(url_for('userScreening'))
    else:
        #Redirecting back to register page if the input values are not correct
        flash('An error occured while handling your request... Please try again.', 'error')
        return(redirect(url_for('userScreening')))

@app.route('/user')
def userScreening():
    if(session.get('name')):
        courses = getCourses()
        #TODO: Render different page based on user type
        return render_template('userScreening.html', session = session, roleOptions = roleOptions, courses = courses)
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

def getCourses():
    '''Gets all courses from database'''
    global courses
    connection = connectToDB()
    cursor = connection.cursor()

    cursor.execute("select nomeCorso from Corso")
    #Clearing courses list in order to correctly store all available courses
    courses = []
    for course in cursor:
        #Getting the first element of each row
        courses.append(course[0])
    return courses

@app.route('/user/logout')
def logout():
    #Checking if session exists before clearing it
    if(session.get('name')):
        session.clear()
        flash("Successfully logged out.", 'success')
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug = True)
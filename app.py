from flask import Flask, render_template, url_for, request, redirect, session,flash, Response
from argon2 import PasswordHasher, exceptions
import mysql.connector
from authlib.integrations.flask_client import OAuth
from authlib.integrations.base_client.errors import OAuthError
from datetime import datetime


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
            flash("The registration service is having problems... Please try reloading the page or try again later", 'error')
            return redirect(url_for('login'))
        cursor = connection.cursor()
        #Getting all data from the database related to that single email (representing PRIMARY KEY)
        cursor.execute('select * from Utente where Email = %(email)s', {'email': email})
        
        response = cursor.fetchone()
        #`response == None` means that no user with the input email was found in the database
        if(response == None):
            flash("Account not found", 'error')
            return redirect(url_for('login'))
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
            session['email'] = response[0]
            session['name'] = response[1]
            session['surname'] = response[2]
            session['role'] = response[4]
            session['course'] = response[5]
            #Reformatting last login date for clean output
            session['lastLogin'] = str(response[8]).replace(' ', ' alle ')

            #Default last login value in database = fresh account so a new password needs to be set. Redirecting to password creation page
            if(session['lastLogin'] == 'Mai'):
                return redirect(url_for('updatePassword'))
            else:
                #Updating last login time and redirecting user to screening
                updateLastLoginTime()
                return redirect(url_for('userScreening'))
        finally:
            connection.close()
            cursor.close()
    else:
        flash("An error occured while submitting the form. Please try again.", 'error')
    return redirect(url_for('login'))

@app.route('/user/updatepassword')
def updatePassword():
    '''Lets the user update his freshly created account's password'''
    return render_template('updatePassword.html')

@app.route('/user/updatepassword/verify', methods = ['GET', 'POST'])
def verify_updated_password():
    if(request.form.get('newPassword')):
        newPassword = request.form.get('newPassword')
        #Checking if form's passwords match, otherwise redirecting back to correct it
        if(newPassword == request.form.get('passwordVerify')):
            #TODO: Check for possible `False` returned value
            connection = connectToDB()
            cursor = connection.cursor()
            pHasher = PasswordHasher()
            cursor.execute('select PW from Utente where Email = %(email)s', {'email': session['email']})
            response = cursor.fetchone()
            try:
                pHasher.verify(str(response[0]), newPassword)
            #New and old passwords must be different, so the error must be triggered when `verifyMismatchError` is not raised
            except exceptions.VerifyMismatchError:
                pass
            else:
                flash("Password cannot be the same as before, try again", 'error')
                return redirect(url_for('updatePassword'))
            hashedPW = pHasher.hash(newPassword.encode())
            
            session['lastLogin'] = updateLastLoginTime()
            cursor.execute("update Utente set PW = %(newPW)s where Email = %(userEmail)s", {'newPW': hashedPW, 'userEmail': session['email']})
            connection.commit()
            cursor.close()
            connection.close()
            return redirect(url_for('userScreening'))
        else:
            flash('Passwords not matching', 'error')
        return redirect(url_for('updatePassword'))
    else:
        flash("Please try again", 'error')
        return redirect(url_for('updatePassword'))

@app.route('/auth/github')
def githubAuth():
    if(session.get('name')):
        #NOTE: `_external` means that it's pointing to an external domain
        return oauth.github.authorize_redirect(url_for('authorize', _external = True))
    else:
        flash('You must login first', 'error')
        return redirect(url_for('login'))

@app.route('/auth/github/callback')
def authorize():
    if(session.get('name')):
        #TODO: Add user's unique ID to database
        try:
            oauth.github.authorize_access_token()
            profile = oauth.github.get('user').json()
        except OAuthError:
            flash('Link with GitHub failed', 'error')
            return redirect(url_for('login'))
        #Checking if user has already linked a github account, otherwise the account linking function will be called
        if(not checkUserGithubConnection()):
            flash('Account linked successfully', 'success')
            linkGithubAccount(profile['id'])
        else:
            flash('Account already linked', 'error')
        return redirect(url_for('userScreening'))
    else:
        flash('You must login first', 'error')
        return redirect(url_for('login'))

@app.route('/user')
def userScreening():
    if(session.get('name')):
        #Redirecting to update password page if it's the first login
        if(session.get('lastLogin') == 'Mai'):
            return redirect(url_for('updatePassword'))
        courses = getCourses()
        return render_template('userScreening.html', session = session, roleOptions = roleOptions, courses = courses)
    else:
        flash('Please login', 'error')
        return redirect(url_for('login'))

@app.route('/user/create', methods = ['GET', 'POST'])
def handle_request():
    #TODO: Make async request
    #TODO: Check for user role to be ADMIN before processing account creation
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

        try:
            cursor.execute('insert into Utente(Email, Nome, Cognome, PW, Tipologia, nomeCorso) values(%(email)s, %(name)s, %(surname)s, %(pw)s, %(role)s, %(course)s)', {'email': email, 'name': fname, 'surname': lname, 'pw': hashedPW, 'role': role, 'course': course})
            #Sending request to DB
            connection.commit()
        #`IntegrityError` means that one or more contraint rules were not met
        except mysql.connector.errors.IntegrityError:
            flash('User with this email already exists', 'error')
        else:
            flash('Account created', 'success')
        #Closing connection
        cursor.close()
        connection.close()
        return redirect(url_for('userScreening'))
    else:
        #Redirecting back to register page if the input values are not correct
        flash('An error occured while handling your request... Please try again.', 'error')
        return(redirect(url_for('userScreening')))

@app.route('/user/logout')
def logout():
    #Checking if session exists before clearing it
    if(session.get('name')):
        updateLastLoginTime()
        session.clear()
        flash("Successfully logged out.", 'success')
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

def updateLastLoginTime():
    '''Programmatically updates user's last login time on database'''
    #TODO: Update with GMT+1 timezone
    timeNow = datetime.now()
    timeNow = timeNow.strftime('%d-%m-%Y %H:%M')

    connection = connectToDB()
    cursor = connection.cursor()
    cursor.execute("update Utente set UltimoLogin = %(timeNow)s where Email = %(userEmail)s", {'timeNow': timeNow, 'userEmail': session['email']})
    connection.commit()
    cursor.close()
    connection.close()
    return str(timeNow).replace(' ', ' alle ')

def checkUserGithubConnection():
    '''Checks if the user has a linked Github account'''
    connection = connectToDB()
    cursor = connection.cursor()
    response = cursor.execute('select github_id from Utente where Email = %(userEmail)s', {'userEmail': session['email']})
    print(response)
    if(not response):
        returnedValue = False
    else:
        returnedValue = True
    connection.close()
    return returnedValue
    
def linkGithubAccount(userID):
    #TODO: Check on all DB accounts for that user id
    connection = connectToDB()
    cursor = connection.cursor()
    #Updating table column with github user id
    cursor.execute("update Utente set github_id = %(github_userID)s where Email = %(userEmail)s", {'github_userID': userID, 'userEmail': session['email']})
    connection.commit()
    connection.close()

if __name__ == "__main__":
    app.run(debug = True)
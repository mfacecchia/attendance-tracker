from flask import Flask, render_template, url_for, request, redirect, session,flash, Response
from argon2 import PasswordHasher, exceptions
import mysql.connector
from authlib.integrations.flask_client import OAuth
from authlib.integrations.base_client.errors import OAuthError
from datetime import datetime
from os import environ

app = Flask(__name__)
oauth = OAuth(app)
app.config['SECRET_KEY'] = environ['FLASK_SECRET']
app.config['SESSION_TYPE'] = 'filesystem'

#GITHUB CONFIG DATA
app.config['GITHUB_CLIENT_ID'] = environ['GITHUB_CLIENT_ID']
app.config['GITHUB_CLIENT_SECRET'] = environ['GITHUB_CLIENT_SECRET']
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
commonErrorMessage = 'An error occured while handling your request... Please try again.'

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
    '''Handler for User login request'''
    if(request.form.get('email') and request.form.get('password')):
        email = request.form.get('email')
        pw = request.form.get('password')
        
        connection = connectToDB()
        if(not connection):
            return redirect(url_for('index'))
        cursor = connection.cursor()
        #Getting all data from the database related to that single email (representing Unique key)
        cursor.execute('select Utente.userID, Nome, Tipologia, ultimoLogin, Email, PW, githubID, googleID\
                                from Credenziali, Utente\
                                where Credenziali.userID = Utente.userID\
                                and Email = %(email)s', {'email': email})
        response = getValuesFromQuery(cursor)
        if(len(response) == 0):
            flash("Account not found", 'error')
            return redirect(url_for('login'))
        phasher = PasswordHasher()
        try:
            #Verifying the hashed password gotten from the database with the user input one in the form
            phasher.verify(response[0]['PW'], pw)
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
            session['uid'] = response[0]['userID']
            session['name'] = response[0]['Nome']
            session['role'] = response[0]['Tipologia']
            #Reformatting last login date for clean output
            session['lastLogin'] = str(response[0]['ultimoLogin']).replace(' ', ' alle ')
            session['githubConnected'] = True if response[0]['githubID'] != 'NULL' else False

            #Default last login value in database = fresh account so a new password needs to be set. Redirecting to password creation page
            if(session['lastLogin'] == 'Mai'):
                return redirect(url_for('updatePassword'))
            else:
                #Updating last login time and redirecting user to screening
                updateLastLoginTime()
                return redirect(url_for('userScreening'))
        finally:
            connection.close()
    else:
        flash(commonErrorMessage, 'error')
    return redirect(url_for('login'))

@app.route('/user/updatepassword')
def updatePassword():
    '''Lets the user update his freshly created account's password'''
    return render_template('updatePassword.html')

@app.route('/user/updatepassword/verify', methods = ['GET', 'POST'])
def verify_updated_password():
    newPassword = request.form.get('newPassword')
    if(newPassword != None and len(newPassword) >= 10):
        #Checking if form's passwords match, otherwise redirecting back to correct it
        if(newPassword == request.form.get('passwordVerify')):
            connection = connectToDB()
            if(not connection):
                return redirect(url_for('index'))
            cursor = connection.cursor()
            pHasher = PasswordHasher()
            #Getting the current password from the user
            cursor.execute('select PW from Credenziali\
                        where userID = %(uid)s', {'uid': session['uid']})
            response = getValuesFromQuery(cursor)
            try:
                pHasher.verify(str(response[0]['PW']), newPassword)
            #New and old passwords must be different, so the error must be triggered when `verifyMismatchError` is not raised
            except exceptions.VerifyMismatchError:
                pass
            else:
                flash("Password cannot be the same as before, try again", 'error')
                return redirect(url_for('updatePassword'))
            hashedPW = pHasher.hash(newPassword.encode())
            cursor.execute("update Credenziali set PW = %(newPW)s\
                        where userID = %(uid)s", {'newPW': hashedPW, 'uid': session['uid']})
            connection.commit()
            session['lastLogin'] = updateLastLoginTime()
            connection.close()
            return redirect(url_for('userScreening'))
        else:
            flash('Passwords not matching', 'error')
        return redirect(url_for('updatePassword'))
    else:
        flash("Please try again", 'error')
        return redirect(url_for('updatePassword'))

@app.route('/auth/github', methods = ['GET'])
def githubAuth():
    login = request.args.get('login')
    #NOTE: `_external` means that it's pointing to an external domain
    return oauth.github.authorize_redirect(url_for('authorize', _external = True, login = [login]))

@app.route('/auth/github/callback', methods = ['GET'])
def authorize():
    #Converting the `login` request from the URL to a boolean value
    #Obtaining the value from URL as a GET parameter
    login = True if request.args.get('login') == 'True' else False
    #Getting the user values and starting the OAuth autorization process
    try:
        oauth.github.authorize_access_token()
        profile = oauth.github.get('user').json()
    except OAuthError:
        flash('Request failed', 'error')
        return redirect(url_for('login'))
    #`not login` = `False` means that the service requested is github account link (account already linked)
    if(not login):
        if(session.get('name')):
            #Checking if user has already linked a github account, otherwise the account linking function will be called
            if(not checkUserGithubConnection()):
                if(linkGithubAccount(profile['id'])):
                    flash('Account linked successfully', 'success')
                else:
                    flash('This github account is already used... Please try using a different one.', 'error')
            else:
                flash('Account already linked', 'error')
            return redirect(url_for('userScreening'))
        else:
            flash('You must login first', 'error')
            return redirect(url_for('login'))
    #Requested login with github account
    else:
        #Account found, so redirecting to user screening page
        if(loginWithGithub(profile['id'])):
            return redirect(url_for('userScreening'))
        #Redirecting to login page if the account was not found
        flash("Account not found", 'error')
        return redirect(url_for('login'))

@app.route('/auth/github/disconnect')
def unlinkGithubAccount():
    #Checks if the logged user has a linked github account
    if(session.get('githubConnected')):
        connection = connectToDB()
        if(not connection):
            return redirect(url_for('index'))
        cursor = connection.cursor()
        cursor.execute('update Credenziali set githubID = NULL\
                    where userID = %(uid)s', {'uid': session['uid']})
        connection.commit()
        session['githubConnected'] = False
        flash('Github account unlinked', 'success')
    return redirect(url_for('userScreening'))

@app.route('/user')
def userScreening():
    if(session.get('name')):
        #Redirecting to update password page if it's the first login
        if(session.get('lastLogin') == 'Mai'):
            return redirect(url_for('updatePassword'))
        getCourses()
        return render_template('userScreening.html', session = session, roleOptions = roleOptions, courses = courses)
    else:
        flash('Please login', 'error')
        return redirect(url_for('login'))

@app.route('/user/create', methods = ['GET', 'POST'])
def handle_request():
    #TODO: Make async request
    if(request.form.get('role') in roleOptions and len(request.form.getlist('course')) > 0):
        fname = request.form.get('fname').strip().capitalize()
        lname = request.form.get('lname').strip().capitalize()
        email = request.form.get('email').strip().lower()
        pw = request.form.get('password')
        role = request.form.get('role')
        chosenCourses = request.form.getlist('course')

        coursesNames = []
        coursesYears = []
        for course in chosenCourses:
            coursesNames.append(course.split(" - ")[0])
            coursesYears.append(course.split(" - ")[1])
        #Validating the chosen courses
        if(validateCoursesSelection(coursesNames, coursesYears)):
            #Checking if all the form fields input are not empty and the password contains at least 10 characters before proceeding
            if(validateFormInput(fname, lname, email, pw) and len(pw) >= 10):
                pHasher = PasswordHasher()
                pw = pw.encode()
                hashedPW = pHasher.hash(pw)

                connection = connectToDB()
                if(not connection):
                    return redirect(url_for('index'))
                #Creating a cursor reponsible for query executions
                cursor = connection.cursor()
                #Checking if user with the input Email does not already exist
                cursor.execute("select Email from Credenziali where Email = %(userEmail)s", {'userEmail': email})
                response = getValuesFromQuery(cursor)
                if(len(response) == 0):
                    #Matrix with all the queries to execute to create the account
                    queries = [
                                ['insert into Utente(Nome, Cognome, Tipologia) values(%(name)s, %(surname)s, %(role)s)', {'name': fname, 'surname': lname, 'role': role}],
                                ['insert into Credenziali(Email, PW, userID) values(%(email)s, %(pw)s, (select max(userID) from Utente))', {'email': email, 'pw': hashedPW}],
                            ]
                    #Executing all queries from the pre-created matrix
                    for query in queries:
                        cursor.execute(query[0], query[1])
                        #Sending request to DB
                        connection.commit()
                    for x in range(len(coursesNames)):
                        cursor.execute('insert into Registrazione(userID, idCorso) values((select max(userID) from Utente), (select idCorso from Corso where nomeCorso = %(courseName)s and annoCorso = %(courseYear)s))', {'courseName': coursesNames[x], 'courseYear': coursesYears[x]})
                        connection.commit()
                    flash('Account created', 'success')
                else:
                    flash('User with this email already exists', 'error')
                #Closing connection
                connection.close()
                return redirect(url_for('userScreening'))
            else:
                flash('Wrong courses values. Please try again', 'error')
                return(redirect(url_for('userScreening')))
    #Redirecting back to register page if the input values are not correct
        else:
            flash('Please select at least one valid course from the list', 'error')
            return(redirect(url_for('userScreening')))
    else:
        flash('Please select a valid role and at least one course from the menu')
        return(redirect(url_for('userScreening')))

@app.route('/lesson/create', methods = ['GET', 'POST'])
def createLesson():
    return "Processing"

@app.route('/user/list')
def usersList():
    if(session['role'] == 'Admin'):
        usersList = getUsersList()
        return render_template('usersList.html', users = usersList)

@app.route('/user/select', methods = ['GET', 'POST'])
def select_user():
    if(session['role'] == 'Admin'):
        if(request.values.get('userID')):
            uid = request.values.get('userID')
            selectedUser = getUserData(uid)
            getCourses()
            return render_template('userData.html', userData = selectedUser, courses = courses, roles = roleOptions)
    return redirect(url_for('userScreening'))

@app.route('/user/update', methods = ['GET', 'POST'])
def update_user_data():
    if(session['role'] == 'Admin'):
        #FIXME: Fix function `updateDataAsAdmin()`
        userID = updateDataAsAdmin()
        return redirect(url_for('select_user', userID = userID))
    else:
        pass
    #Redirecting back to register page if the input values are not correct
    flash(commonErrorMessage, 'error')
    return(redirect(url_for('usersList')))

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
        connection = mysql.connector.connect(user = environ['DB_USERNAME'], password = environ['DB_PWORD'], host = environ['DB_HOSTNAME'], database = environ['DB_NAME'])
    except mysql.connector.Error:
        flash('The service is having some problems at the moment. Please try again later', 'error')
        return False
    return connection

def getCourses():
    '''Gets all courses from database'''
    global courses
    connection = connectToDB()
    if(not connection):
        return redirect(url_for('index'))
    cursor = connection.cursor()
    cursor.execute("select nomeCorso, annoCorso from Corso")
    #Overwriting list with newly values from DB response
    courses = getValuesFromQuery(cursor)

def getValuesFromQuery(cursor):
    '''Returns the DB response in form of list of dictionaries\n
    Takes as parameter a response from `cursor.execute()`'''
    responseDict = []
    for row in cursor:
        #Creating a dictionary for each row of the DB response
        responseDict.append({})
        for colCounter, col in enumerate(row):
            responseDict[-1].setdefault(cursor.description[colCounter][0], col)
    return responseDict

def updateLastLoginTime():
    '''Programmatically updates user's last login time on database'''
    #TODO: Update with GMT+1 timezone
    timeNow = datetime.now()
    #TODO: Update format with `%d/%m/%Y %H:%M`
    timeNow = timeNow.strftime('%d-%m-%Y %H:%M')

    connection = connectToDB()
    if(not connection):
        return redirect(url_for('index'))
    cursor = connection.cursor()
    cursor.execute("update Utente set ultimoLogin = %(timeNow)s where userID = %(uid)s", {'timeNow': timeNow, 'uid': session['uid']})
    connection.commit()
    cursor.close()
    connection.close()
    return str(timeNow).replace(' ', ' alle ')

def checkUserGithubConnection():
    '''Checks if the user has a linked Github account'''
    connection = connectToDB()
    if(not connection):
        return redirect(url_for('index'))
    cursor = connection.cursor()
    response = cursor.execute('select githubID from Utente where userID = %(uid)s', {'uid': session['uid']})
    if(not response):
        returnedValue = False
    else:
        returnedValue = True
    connection.close()
    return returnedValue
    
def linkGithubAccount(userID):
    connection = connectToDB()
    if(not connection):
        return redirect(url_for('index'))
    cursor = connection.cursor()
    #Checking if the github user ID is already in the database (same UID cannot be used my more than 1 person)
    cursor.execute('select githubID from Utente where githubID = %(github_userID)s', {'github_userID': userID})
    response = cursor.fetchone()
    #`response = None` means no one has linked that specific account
    if(response != None):
        accountLinked = False
    else:
        #Updating table column with github user id
        cursor.execute("update Utente set githubID = %(github_userID)s where userID = %(uid)s", {'github_userID': userID, 'uid': session['uid']})
        connection.commit()
        session['githubConnected'] = True
        accountLinked = True
    connection.close()
    return accountLinked

def loginWithGithub(userID):
    '''Lets the user login with a valid linked github account'''
    connection = connectToDB()
    if(not connection):
        return redirect(url_for('index'))
    cursor = connection.cursor()
    #Finding between all `Utente`'s table columns for a matching github user ID and storing its relative data in a session
    #FIXME: Nonetype
    cursor.execute("select userID, Nome, Cognome, Tipologia, githubID, idCorso, ultimoLogin from Utente where githubID = %(github_userID)s", {'github_userID': str(userID)})
    #Checking for `response != None` in case the Query returns no columns so returned value = None
    if(response != None):
        response = list(cursor.fetchone())
        if(str(response[4]) == str(userID)):
            response[5] = idToCourseName(cursor, response[5])
            session['uid'] = response[0]
            session['name'] = response[1]
            session['surname'] = response[2]
            session['role'] = response[3]
            session['course'] = response[5]
            #Reformatting last login date for clean output
            session['lastLogin'] = str(response[6]).replace(' ', ' alle ')
            session['githubConnected'] = True
            accountFound = True
        else:
            accountFound = False
    #Returning `False` if the github user ID was not found in the table
    else:
        accountFound = False
    connection.close()
    return accountFound

def validateFormInput(*args):
    '''Validates form user input by checking if the input data is not an empty string'''
    for inputValue in args:
        if(inputValue.replace(' ', '') == ''):
            return False
    return True

def getUsersList():
    '''Obtains all users from the database and returns a matrix'''
    connection = connectToDB()
    if(not connection):
        return redirect(url_for('index'))
    cursor = connection.cursor()
    cursor.execute("select Utente.userID, Nome, Cognome, Tipologia, nomeCorso\
                from Utente\
                inner join Registrazione on Utente.userID = Registrazione.userID\
                inner join Corso on Registrazione.idCorso = Corso.idCorso\
                group by(userID)")
    usersList = getValuesFromQuery(cursor)
    connection.close()
    return usersList

def getUserData(uid):
    connection = connectToDB()
    if(not connection):
        return redirect(url_for('index'))
    cursor = connection.cursor()

    cursor.execute('select Utente.userID, Nome, Cognome, Tipologia, Email, nomeCorso, annoCorso\
                from Utente\
                inner join Credenziali on Utente.userID = Credenziali.userID\
                inner join Registrazione on Registrazione.userID = Utente.userID\
                inner join Corso on Corso.idCorso = Registrazione.idCorso\
                where Utente.userID = %(uid)s', {'uid': int(uid)})
    response = getValuesFromQuery(cursor)
    
    #Getting all courses from the query and creating a single list with all the obtained ones
    response[0]['nomeCorso'] = [response[0]['nomeCorso']]
    for course in response[1:]:
        response[0]['nomeCorso'].append(course['nomeCorso'])
    connection.close()
    return response[0]

#TODO: Remove function (no longer useful)
def idToCourseName(cursor, courseID):
    '''Converts course ID to course name based on Foreign key <--> Primary key relation'''
    cursor.execute('select nomeCorso from corso where idCorso = %(courseID)s', {'courseID': int(courseID)})
    return cursor.fetchone()[0]

def updateDataAsAdmin():
    '''Shorthand function to update any user data as administrator'''
    if(request.form.get('role') in roleOptions and request.form.get('course') in courses):
        fname = request.form.get('fname').strip().capitalize()
        lname = request.form.get('lname').strip().capitalize()
        email = request.form.get('email').strip().lower()
        userID = request.form.get('uid')
        role = request.form.get('role')
        courseName = request.form.get('course')

        #Checking if all the form fields input are not empty
        if(validateFormInput(fname, lname, email)):

            connection = connectToDB()
            if(not connection):
                return redirect(url_for('index'))
            #Creating a cursor reponsible for query executions
            cursor = connection.cursor()

            cursor.execute('select idCorso from Corso where nomeCorso = %(courseName)s', {'courseName': courseName})
            courseID = cursor.fetchone()[0]

            try:
                cursor.execute('update Utente set Nome = %(fname)s, Cognome = %(lname)s, Email = %(email)s, Tipologia = %(role)s, idCorso = %(courseID)s where userID = %(uid)s', {'fname': fname, 'lname': lname, 'email': email, 'role': role, 'courseID': courseID, 'uid': userID})
                #Sending request to DB
                connection.commit()
            #`IntegrityError` means that one or more contraint rules were not met
            except mysql.connector.errors.IntegrityError:
                flash('User with this email already exists', 'error')
            else:
                flash('Account updated', 'success')
            #Closing connection
            connection.close()
        else:
            flash('Invalid input. Please try again.', 'error')
    else:
        flash('Please select a valid role and course from the menus')
    return userID

def validateCoursesSelection(coursesNames, coursesYears):
    '''Gets all courses names and relative years as parameters and executes a query for each item to check if the actual selection exists\n
    Returns `False` if the DB response returns `None`, else `True` if all requests return a value'''
    connection = connectToDB()
    if not connection:
        return False
    cursor = connection.cursor()
    for course in range(len(coursesNames)):
        cursor.execute("select count(*)\
                    from Corso\
                    where nomeCorso = %(courseName)s and annoCorso = %(courseYear)s", {'courseName': coursesNames[course], 'courseYear': coursesYears[course]})
        if(cursor.fetchone()[0] == 0):
            return False
    return True


if __name__ == "__main__":
    app.run(debug = True)
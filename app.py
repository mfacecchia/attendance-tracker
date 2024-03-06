from flask import Flask, render_template, url_for, request, redirect, session,flash, jsonify
from flask_mail import Mail, Message, BadHeaderError
from argon2 import PasswordHasher, exceptions
import mysql.connector
from authlib.integrations.flask_client import OAuth
from authlib.integrations.base_client.errors import OAuthError
from datetime import datetime, date, timedelta
from base64 import urlsafe_b64encode, urlsafe_b64decode
from binascii import Error as conversionError
from os import environ

app = Flask(__name__)
oauth = OAuth(app)

app.config['SECRET_KEY'] = environ['FLASK_SECRET']
app.config['SESSION_TYPE'] = 'filesystem'

app.config['MAIL_SERVER'] = environ['MAIL_SERVER']
app.config['MAIL_PORT'] = environ['MAIL_PORT']
app.config['MAIL_USERNAME'] = environ['MAIL_USERNAME']
app.config['MAIL_PASSWORD'] = environ['MAIL_PASSWORD']
app.config['MAIL_USE_TLS'] = True
mailer = Mail(app)

#Registering OAuth application for future requests
oauth.register(
    'github',
    client_id = environ['GITHUB_CLIENT_ID'],
    client_secret = environ['GITHUB_CLIENT_SECRET'],
    access_token_url = 'https://github.com/login/oauth/access_token',
    authorize_url = 'https://github.com/login/oauth/authorize',
    api_base_url = 'https://api.github.com/',
    client_kwargs = {'scope': 'user:email'}
)

#List of roles available for the registration
roleOptions = ['Studente', 'Insegnante', 'Admin']
#Creating a variable used to store all available courses from the database and pass them to the HTML template
courses = []
lessonTypes = ['Lezione', 'Seminario', 'Laboratorio']
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
        cursor.execute('select Utente.userID, Nome, Tipologia, ultimoLogin, PW, githubID, googleID\
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
            session['lastLogin'] = response[0]['ultimoLogin'].replace(' ', ' alle ')
            session['githubConnected'] = bool(response[0]['githubID'])

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

@app.route('/forgot-password', methods = ['GET', 'POST'])
def forgotPassword():
    #TODO: Add db field in `Credenziali` called = `passwordDimenticata` with `False` as default value
    email = request.form.get('email')
    #If the form has not been submitted, the first redirect will be to the form for inputting the user's email, otherwise proceeding with user verification
    if(email):
        #Checking if the user exist by getting its relative userID from the database
        uid = verifyUserExistence(email)
        flash('You will shortly receive a reset password email if it\'s registered', 'success')
        if(uid):
            #Getting the dictionary's `userID` key's value and parsing it to string
            uid = str(uid['userID'])
            message = Message(subject = 'Recupera Password',
                            recipients = [email],
                            #TODO: Decode after email is sent, not before
                            html = render_template('recoverPasswordTemplate.html', userMail = b64_encode_decode(email).decode(), userID = b64_encode_decode(uid).decode()),
                            sender = ('Attendance Tracker Mailing System', environ['MAIL_USERNAME'])
                            )
            try:
                mailer.send(message)
            #Avoiding HTTP Header injections
            except BadHeaderError:
                flash('There was an error while sending the email. Please try again', 'error')
        return redirect(url_for('login'))
    else:
        return render_template('reset-password-form.html')

@app.route('/user/updatepassword', methods = ['GET'])
def updatePassword():
    '''Lets the user update his freshly created account's password'''
    userEmail = request.args.get('mail')
    userID = request.args.get('uid')
    if(userEmail and userID):
        userEmail = b64_encode_decode(userEmail, False)
        userID = b64_encode_decode(userID, False)
        #Managing conversion error with redirect to login page if `b64_encode_decode` function returns `False`
        if(not userEmail or not userID):
            flash('An error occured. Please try again', 'error')
            return redirect(url_for('login'))
        #Query `count` result = 1 means account found so redirecting to update password
        if(verifyUserExistence(userEmail, userID)['result'] == 1):
            session['uid'] = userID
            return render_template('updatePassword.html')
        else:
            flash('This user does not exist.', 'error')
            return redirect(url_for('login'))
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
            flash('Password updated!', 'success')
            return redirect(url_for('login'))
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
                    flash('This github account is already linked to a different user... Please try using a different one.', 'error')
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
        connection.close()
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
        response = []
        scheduledLessons = []
        #Getting teacher's courses to display in the lesson creation section
        if(session.get('role') == 'Insegnante'):
            connection = connectToDB()
            cursor = connection.cursor()
            cursor.execute('select nomeCorso, annoCorso\
                        from Corso\
                        inner join Registrazione on Corso.idCorso = Registrazione.idCorso\
                        inner join Utente on Registrazione.userID = Utente.userID\
                        where Utente.userID = %(uid)s', {'uid': session['uid']})
            response = getValuesFromQuery(cursor)
            connection.close()
        scheduledLessons = getLessonsList()
        return render_template('userScreening.html',
                            session = session,
                            roleOptions = roleOptions,
                            courses = courses if not response else response,
                            lessonTypes = lessonTypes,
                            helloMessage = getCustomMessage(),
                            currentYear = int(datetime.now().strftime('%Y')),
                            scheduledLessons = scheduledLessons,
                            today = date.today()
                        )
    else:
        flash('Please login', 'error')
        return redirect(url_for('login'))

@app.route('/user/create', methods = ['GET', 'POST'])
def createUser():
    #TODO: Make async request
    if(session.get('role') == 'Admin'):
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
                    #Checking for actual values length to avoid DB values limits
                    if(len(fname) <= 20 and len(lname) <= 20 and len(email) <= 40):
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
                            #TODO: Add default lesson attendance column in `Partecipazione` table for lessons after the current date
                            queries = [
                                        ['insert into Utente(Nome, Cognome, Tipologia) values(%(name)s, %(surname)s, %(role)s)', {'name': fname, 'surname': lname, 'role': role}],
                                        ['insert into Credenziali(Email, PW, userID) values(%(email)s, %(pw)s, (select max(userID) from Utente))', {'email': email, 'pw': hashedPW}],
                                    ]
                            #Executing all queries from the pre-created matrix
                            for query in queries:
                                cursor.execute(*query)
                                #Sending request to DB
                                connection.commit()
                            cursor.execute('select max(userID) as "userID" from Utente')
                            userID = getValuesFromQuery(cursor)[0]['userID']
                            response = []
                            for x in range(len(coursesNames)):
                                cursor.execute('insert into Registrazione(userID, idCorso) values((select max(userID) from Utente), (select idCorso from Corso where nomeCorso = %(courseName)s and annoCorso = %(courseYear)s))', {'courseName': coursesNames[x], 'courseYear': coursesYears[x]})
                                connection.commit()
                                #Getting all upcoming lesson codes for every user course in order to automatically add a default row in the `Partecipazione` table
                                cursor.execute('select idLezione\
                                            from Lezione\
                                            inner join Corso on Corso.idCorso = Lezione.idCorso\
                                            where dataLezione >= %(dateToday)s\
                                            and nomeCorso = %(selectedCName)s\
                                            and annoCorso = %(selectedCYear)s', {'dateToday': date.today(), 'selectedCName': coursesNames[x], 'selectedCYear': coursesYears[x]})
                                response.append(getValuesFromQuery(cursor))
                            #NOTE: nested `for` loop because the ending `response` format will be a matrix (each list represents a course's set of lessons)
                            for lessonList in response:
                                for lesson in lessonList:
                                    #Adding the user to all lessons
                                    cursor.execute('insert into Partecipazione(userID, idLezione) values(%(uid)s, %(lessonID)s)', {'uid': userID, 'lessonID': lesson['idLezione']})
                                    connection.commit()
                            flash('Account created', 'success')
                        else:
                            flash('User with this email already exists', 'error')
                        #Closing connection
                        connection.close()
                    else:
                        flash('Wrong input values. Please try again', 'error')
                else:
                    flash('Wrong input values. Please try again', 'error')
        #Redirecting back to register page if the input values are not correct
            else:
                flash('Please select at least one valid course from the list', 'error')
        else:
            flash('Please select a valid role and at least one course from the menu')
    else:
        flash(commonErrorMessage, 'error')
    return(redirect(url_for('userScreening')))

@app.route('/lesson/create', methods = ['GET', 'POST'])
def createLesson():
    if(session.get('role') in ['Insegnante', 'Admin']):
        if(request.form.get('lessonType') in lessonTypes and len(request.form.get('room')) == 4):
            subject = request.form.get('subject').strip().capitalize()
            description = request.form.get('description').strip()
            lessonDate = request.form.get('lessonDate')
            lessonRoom = request.form.get('room').upper()
            lessonType = request.form.get('lessonType')
            chosenCourseName, chosenCourseYear = request.form.get('course').split(' - ')
            if(validateCoursesSelection([chosenCourseName], [chosenCourseYear])):
                if(validateFormInput(subject, lessonDate, lessonRoom)):
                    connection = connectToDB()
                    cursor = connection.cursor()
                    cursor.execute('insert into Lezione(Materia, Descrizione, dataLezione, Aula, Tipologia, idCorso) values\
                                (%(subjectName)s, %(description)s, %(lessonDate)s, %(lessonRoom)s, %(lessonType)s, (select idCorso from Corso where nomeCorso = %(courseName)s and annoCorso = %(courseYear)s))', {'subjectName': subject, 'description': description, 'lessonDate': lessonDate, 'lessonRoom': lessonRoom, 'lessonType': lessonType, 'courseName': chosenCourseName, 'courseYear': chosenCourseYear})
                    connection.commit()
                    #Getting all users attending the lesson's course and adding them all to the `Partecipazione` table with default `Presenza` value (`0` or `False`)
                    usersList = selectUsersFromCourse(chosenCourseName, chosenCourseYear)
                    cursor.execute('select max(idLezione) from Lezione')
                    latestLesson = cursor.fetchone()[0]
                    #TODO: Make async request
                    for user in usersList:
                        cursor.execute('insert into Partecipazione(userID, idLezione) values(%(uid)s, %(latestLessonID)s)', {'uid': user['userID'], 'latestLessonID': latestLesson})
                        connection.commit()
                    connection.close()
                    flash('Lesson created', 'success')
                else:
                    flash('Wrong input values. Please try again.', 'error')
            else:
                flash('Course not found. Please try again.', 'error')
        else:
            flash('Please select a valid lesson type and course from the menus', 'error')
    else:
        flash(commonErrorMessage, 'error')
    return redirect(url_for('login'))

@app.route('/lesson', methods = ['GET'])
def manageLesson():
    if(session.get('role') in ['Admin', 'Insegnante']):
        try:
            lessonID = int(request.args.get('id'))
        except ValueError:
            return redirect(url_for('userScreening'))
        connection = connectToDB()
        cursor = connection.cursor()
        cursor.execute('select Utente.userID, Nome, Cognome, Materia, dataLezione, Lezione.idLezione, Presenza\
                    from Utente\
                    inner join Partecipazione on Utente.userID = Partecipazione.userID\
                    inner join Lezione on Partecipazione.idLezione = Lezione.idLezione\
                    where Utente.Tipologia = "Studente"\
                    and Lezione.idLezione = %(lessonID)s', {'lessonID': lessonID})
        response = getValuesFromQuery(cursor)
        if(not response):
            flash('No entries found for the selected lesson', 'error')
            return redirect(url_for('userScreening'))
        #Converting all gotten dates to a more user friendly format
        for lessonDate in response:
            lessonDate['dataLezione'] = lessonDate['dataLezione'].strftime('%d/%m/%Y')
        connection.close()
        return render_template('manageLesson.html', lessonInfo = response)
    else:
        return redirect(url_for('userScreening'))

@app.route('/lesson/register-attendance', methods = ['GET', 'POST'])
def registerAttendances():
    if(session.get('role') in ['Admin', 'Insegnante']):
        selectedLessonID = request.form.get('registerAttendance')
        attendances = request.form.getlist('attendanceCheck')
        connection = connectToDB()
        cursor = connection.cursor()
        #Resetting the the attendance flag from every user in the DB to set the correct values
        cursor.execute('update Partecipazione set Presenza = 0 where idLezione = %(lessonID)s', {'lessonID': selectedLessonID})
        connection.commit()
        for attendance in attendances:
            cursor.execute('update Partecipazione set Presenza = 1 where userID = %(uid)s and idLezione = %(lessonID)s', {'uid': attendance, 'lessonID': selectedLessonID})
            connection.commit()
        connection.close()
        flash('Attendances saved', 'success')
    return redirect(url_for('manageLesson', id = selectedLessonID))

@app.route('/lesson/attendances', methods = ['GET'])
def getAttendancesCount():
    '''API that returns the list of all attended courses attendances count'''
    if(session.get('role') in ['Admin', 'Insegnante']):
        try:
            return getLessonsAttendancesCount(int(request.args.get('range')))
        except ValueError:
            return getLessonsAttendancesCount()
    else:
        return []

@app.route('/lesson/attendances/percentage', methods = ['GET'])
def getAttendancesPercentage():
    '''API that returns the total number of lessons and the total count of attendances'''
    if(session.get('role') == 'Studente'):
        connection = connectToDB()
        if not connection:
            return redirect(url_for('index'))
        try:
            range = int(request.args.get('range'))
        except ValueError:
            range = 7
        #Calculating date range starting from today's date
        dateRange = date.today() - timedelta(days = range)
        cursor = connection.cursor()
        #Obtaining all user attended lessons based on userID and date range previously calculated
        cursor.execute('select Presenza\
                    from Partecipazione\
                    inner join Lezione on Lezione.idLezione = Partecipazione.idLezione\
                    where userID = %(uid)s\
                    and dataLezione between %(dateRange)s and %(dateToday)s', {'uid': session.get('uid'), 'dateRange': dateRange, 'dateToday': date.today()})
        lessons = getValuesFromQuery(cursor)
        attendedLessons = 0
        #Calculating the total number of attended lessons (query returning values are ONLY `0` and `1`)
        for attendance in lessons:
            attendedLessons += attendance['Presenza']
        return jsonify(
            [
                {
                    'total_lessons': len(lessons),
                    'attended_lessons': attendedLessons,
                    'not_attended_lessons': len(lessons) - attendedLessons
                }
            ]
        )
    else:
        return []


@app.route('/course/create', methods = ['GET', 'POST'])
def create_course():
    if(session.get('role') == 'Admin'):
        courseName = request.form.get('courseName').capitalize()
        courseYear = request.form.get('courseYear')
        if(validateFormInput(courseName, courseYear)):
            if(not validateCoursesSelection([courseName], [courseYear])):
                connection = connectToDB()
                if(not connection):
                    return redirect(url_for('index'))
                cursor = connection.cursor()
                cursor.execute('insert into Corso(nomeCorso, annoCorso) values(%(courseName)s, %(courseYear)s)', {'courseName': courseName, 'courseYear': courseYear})
                connection.commit()
                connection.close()
                flash('Course added', 'success')
            else:
                flash('This course already exists. Please try again.', 'error')
        else:
            flash('Invalid input. Please try again.', 'error')
    else:
        flash(commonErrorMessage, 'error')
    return redirect(url_for('userScreening'))

@app.route('/user/list')
def usersList():
    if(session.get('role') == 'Admin'):
        usersList = getUsersList()
        return render_template('usersList.html', users = usersList)

@app.route('/user/select', methods = ['GET', 'POST'])
def select_user():
    if(session.get('role') == 'Admin'):
        uid = request.values.get('userID')
        if(request.form.get('submitButton') == 'Edit'):
            if(request.values.get('userID')):
                selectedUser = getUserData(uid)
                getCourses()
                return render_template('userData.html', userData = selectedUser, courses = courses, roles = roleOptions)
        else:
            deleteUser(uid)
            flash('User removed!', 'success')
            return redirect(url_for('usersList'))
    return redirect(url_for('userScreening'))

@app.route('/user/update', methods = ['GET', 'POST'])
def update_user_data():
    if(session.get('role') == 'Admin'):
        userID = updateDataAsAdmin()
        return redirect(url_for('select_user', userID = userID))
    elif(session.get('role') in ['Studente', 'Insegnante']):
        if(updateDataAsUser()):
            flash('Data updated', 'success')
    else:
        flash(commonErrorMessage, 'error')
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
    timeNow = datetime.now()
    timeNow = timeNow.strftime('%d/%m/%Y %H:%M')

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
    response = cursor.execute('select githubID from Credenziali where userID = %(uid)s', {'uid': session['uid']})
    returnedValue = bool(response)
    connection.close()
    return returnedValue
    
def linkGithubAccount(userID):
    connection = connectToDB()
    if(not connection):
        return redirect(url_for('index'))
    cursor = connection.cursor()
    #Checking if the github user ID is already in the database (same UID cannot be used my more than 1 person)
    cursor.execute('select githubID from Credenziali where githubID = %(github_userID)s', {'github_userID': userID})
    response = cursor.fetchone()
    #`response = None` means no one has linked that specific account
    if(response != None):
        accountLinked = False
    else:
        #Updating table column with github user id
        cursor.execute("update Credenziali set githubID = %(github_userID)s where userID = %(uid)s", {'github_userID': userID, 'uid': session['uid']})
        connection.commit()
        session['githubConnected'] = True
        accountLinked = True
    connection.close()
    return accountLinked

def loginWithGithub(githubUserID):
    '''Lets the user login with a valid linked github account'''
    connection = connectToDB()
    if(not connection):
        return redirect(url_for('index'))
    cursor = connection.cursor()
    #Finding between all `Utente`'s table columns for a matching github user ID and storing its relative data in a session
    cursor.execute("select Utente.userID, Nome, Tipologia, ultimoLogin, Credenziali.githubID\
                from Utente\
                inner join Credenziali on Utente.userID = Credenziali.userID\
                where githubID = %(github_userID)s", {'github_userID': str(githubUserID)})
    response = getValuesFromQuery(cursor)
    #Checking for `response` var content in case the Query returns no columns so returned value = empty list
    if(response and response[0]['githubID'] == str(githubUserID)):
        session['uid'] = response[0]['userID']
        session['name'] = response[0]['Nome']
        session['role'] = response[0]['Tipologia']
        #Reformatting last login date for clean output
        session['lastLogin'] = response[0]['ultimoLogin'].replace(' ', ' alle ')
        session['githubConnected'] = True
        accountFound = True
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
    
    response[0]['nomeCorso'] = getUserCourses(response)
    connection.close()
    return response[0]

def updateDataAsAdmin():
    '''Shorthand function to update any user data as administrator'''
    userID = request.form.get('uid')
    if(request.form.get('role') in roleOptions and len(request.form.getlist('course')) > 0):
        fname = request.form.get('fname').strip().capitalize()
        lname = request.form.get('lname').strip().capitalize()
        email = request.form.get('email').strip().lower()
        pw = request.form.get('password')
        pwVerify = request.form.get('password_verify')
        hashedPW = ''
        role = request.form.get('role')
        chosenCourses = request.form.getlist('course')

        coursesNames = []
        coursesYears = []
        for course in chosenCourses:
            coursesNames.append(course.split(" - ")[0])
            coursesYears.append(course.split(" - ")[1])
        if(validateCoursesSelection(coursesNames, coursesYears)):
            #Checking if all the form fields input are not empty
            if(validateFormInput(fname, lname, email)):
                if(pw != ''):
                    if(len(pw) >= 10 and pw == pwVerify):
                        phasher = PasswordHasher()
                        hashedPW = phasher.hash(pw.encode())
                    else:
                        flash('Passwords not matching or password shorter than 10 characters.', 'error')
                        return userID
                connection = connectToDB()
                if(not connection):
                    return redirect(url_for('index'))
                #Creating a cursor reponsible for query executions
                cursor = connection.cursor()
                cursor.execute('select count(*)\
                            from Credenziali\
                            where Email = %(newEmail)s and userID != %(userID)s', {'newEmail': email, 'userID': userID})
                response = cursor.fetchone()
                if(response[0] == 0):
                    queries = [
                                ['update Utente set Nome = %(name)s, Cognome = %(surname)s, Tipologia = %(role)s where userID = %(uid)s', {'name': fname, 'surname': lname, 'role': role, 'uid': userID}],
                                ['delete from Registrazione where userID = %(uid)s', {'uid': userID}],
                                ['update Credenziali set Email = %(email)s where userID = %(uid)s', {'email': email, 'uid': userID}]
                            ]
                    #Update password only if it has been hashed (valid password input)
                    if(hashedPW):
                        queries.append(['update Credenziali set PW = %(pw)s where userID = %(uid)s', {'pw': hashedPW, 'uid': userID}])
                    for query in queries:
                        cursor.execute(query[0], query[1])
                        connection.commit()
                    for x in range(len(coursesNames)):
                        cursor.execute('insert into Registrazione(userID, idCorso) values(%(uid)s, (select idCorso from Corso where nomeCorso = %(courseName)s and annoCorso = %(courseYear)s))', {'uid': userID, 'courseName': coursesNames[x], 'courseYear': coursesYears[x]})
                        connection.commit()
                    flash('Account updated', 'success')
                else:
                    flash('Email already associated with a different account... Cannot proceed', 'error')
                #Closing connection
                connection.close()
            else:
                flash('Invalid input. Please try again.', 'error')
        else:
            flash('Please select a valid role and course from the menus')
    else:
        flash('Please select a valid role and course from the menus')
    return userID

def updateDataAsUser():
    email = request.form.get('email').strip().lower()
    pw = request.form.get('password')
    pwVerify = request.form.get('password_verify')
    hashedPW = ''
    queries = []
    
    connection = connectToDB()
    if(not connection):
        return redirect(url_for('index'))
    cursor = connection.cursor()
    if(validateFormInput(email) and len(email) <= 40):
        cursor.execute('select count(*)\
                    from Credenziali\
                    where Email = %(newEmail)s', {'newEmail': email})
        response = cursor.fetchone()
        if(response[0] > 0):
            flash('Email already associated with an account... Cannot proceed', 'error')
            return False
        queries.append(['update Credenziali set Email = %(newEmail)s where userID = %(uid)s', {'newEmail': email, 'uid': session['uid']}])
    if(pw != ''):
        if(len(pw) >= 10 and pw == pwVerify):
            phasher = PasswordHasher()
            hashedPW = phasher.hash(pw.encode())
            queries.append(['update Credenziali set PW = %(updatedHashedPW)s where userID = %(userID)s', {'updatedHashedPW': hashedPW, 'userID': session['uid']}])
        else:
            flash('Passwords not matching or password shorter than 10 characters.', 'error')
            return False
    if(not queries):
        flash('No data provided for updating user.', 'error')
        return False
    for query in queries:
        cursor.execute(query[0], query[1])
        connection.commit()
    connection.close()
    return True

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

def getCustomMessage():
    '''Returns a custom message based on the system clock time to be printed out in the user screening page'''
    #Matrix with all the times ranges and the relative printout message
    timesRange = [[0,5, '🌙 Buona notte'],[6,12, '👨‍🏫 Buon giorno'],[13,18, '📚 Buon pomeriggio'],[19,24, '☕️ Buona sera']]
    currentTime = int(datetime.now().strftime('%H'))
    #Iterating through all the list elements and checking the current time range location to obtain the right message
    for timeRange in timesRange:
        if(currentTime >= timeRange[0] and currentTime <= timeRange[1]):
            return timeRange[2]
        
def getUserCourses(response):
    '''Getting all courses from the query and creating a single list with all the obtained ones'''
    response[0]['nomeCorso'] = [response[0]['nomeCorso']]
    for course in response[1:]:
        response[0]['nomeCorso'].append(course['nomeCorso'])
    return response[0]['nomeCorso']

def deleteUser(uid):
    '''Removes a defined user from the database'''
    connection = connectToDB()
    cursor = connection.cursor()
    cursor.execute('delete from Utente where userID = %(uid)s', {'uid': uid})
    connection.commit()
    connection.close()

def getLessonsList():
    connection = connectToDB()
    if(not connection):
        return False
    cursor = connection.cursor()
    #Default query for all user types
    preparedQuery = [
        'select idLezione, Materia, Descrizione, dataLezione, aula, Tipologia, nomeCorso\
        from Lezione\
        inner join Corso on Corso.idCorso = Lezione.idCorso\
        where dataLezione >= %(today)s', {'today': date.today()}
    ]
    #Adding course filter for students and teachers
    if(session.get('role') in ['Studente', 'Insegnante']):
        preparedQuery[0] += ' and Lezione.idCorso in (\
                            select idCorso\
                            from Registrazione\
                            inner join Utente on Utente.userID = Registrazione.userID\
                            where Utente.userID = %(userID)s\
                        )'
        preparedQuery[1].setdefault('userID', session['uid'])
    #Adding the last SQL directives
    preparedQuery[0] += ' order by dataLezione, Materia asc'
    cursor.execute(*preparedQuery)
    response = getValuesFromQuery(cursor)
    #Converting all gotten dates to a more user friendly format
    for lessonDate in response:
        lessonDate['dataLezione'] = lessonDate['dataLezione'].strftime('%d/%m/%Y')
    connection.close()
    return response

def verifyUserExistence(userEmail, userID = None):
    '''Verifies if the user exists before sending the recover password email.\n
    Returns its relative `userID` if the query returns a value, otherwise `False`'''
    connection = connectToDB()
    cursor = connection.cursor()
    if(userID):
        cursor.execute('select count(*) as result from Credenziali where Email = %(userEmail)s and userID = %(uid)s', {'userEmail': userEmail, 'uid': userID})
    else:
        cursor.execute('select userID from Credenziali where Email = %(userEmail)s', {'userEmail': userEmail})
    response = getValuesFromQuery(cursor)
    connection.close()
    if not response:
        return False
    return response[0]

def b64_encode_decode(string:str, encode = True):
    '''Takes a string as input parameter and returns its relative base64 encoded/decoded value'''
    if encode:
        return urlsafe_b64encode(string.encode())
    else:
        try:
            #Decoding to `utf-8` to remove the `b` prefix from string
            return urlsafe_b64decode(string).decode('utf-8')
        #Excepting any type of error while decoding base64 to string
        except conversionError:
            return False

def selectUsersFromCourse(courseName, courseYear):
    '''Executes a query and returns the count of students attending a defined course\
        Returns a list of dictionaries'''
    connection = connectToDB()
    cursor = connection.cursor()
    cursor.execute('select Utente.userID\
                from Corso\
                inner join Registrazione on Registrazione.idCorso = Corso.idCorso\
                inner join Utente on Utente.userID = Registrazione.userID\
                where nomeCorso = %(courseName)s and annoCorso = %(courseYear)s', {'courseName': courseName, 'courseYear': courseYear})
    response = getValuesFromQuery(cursor)
    connection.close()
    return response

def getLessonsAttendancesCount(range = 7):
    '''Executes a query and returns in form of JSON the count of attendances subdivided per lesson date and course id'''
    connection = connectToDB()
    if(not connection):
        return []
    cursor = connection.cursor()
    dateNow = date.today()
    #Getting the analysis start range by subtracting days from today
    dateRange = dateNow - timedelta(days = range)
    #Default query for all user types
    preparedQuery = ['select count(*) as "conteggioPresenze", dataLezione, nomeCorso, annoCorso\
                    from Partecipazione\
                    inner join Lezione on Lezione.idLezione = Partecipazione.idLezione\
                    inner join Corso on Corso.idCorso = Lezione.idCorso\
                    where dataLezione between %(dateRange)s and %(dateToday)s\
                    and Presenza = 1', {'dateRange': dateRange, 'dateToday': dateNow}]
    #Adding course filter for students and teachers
    if(session.get('role') in ['Studente', 'Insegnante']):
        preparedQuery[0] += ' and Lezione.idCorso in (\
                            select idCorso\
                            from Registrazione\
                            inner join Utente on Utente.userID = Registrazione.userID\
                            where Utente.userID = %(userID)s\
                        )'
        preparedQuery[1].setdefault('userID', session['uid'])
    #Adding the last SQL directives
    preparedQuery[0] += ' group by Materia order by dataLezione'
    cursor.execute(*preparedQuery)
    jsonResponse = reformatResponse(getValuesFromQuery(cursor))
    return jsonify(jsonResponse)

def reformatResponse(response):
    '''Gets a list and converts each date to the desired format\
    Returns a list of dictionaries'''
    orderedResponse = []
    for col in response:
        orderedResponse.append({'nomeCorso': f"{col['nomeCorso']} - {col['annoCorso']}", 'dataLezione': col['dataLezione'].strftime('%d/%m/%Y'), 'conteggioPresenze': col['conteggioPresenze']})
    return orderedResponse

if __name__ == "__main__":
    app.run(debug = True)
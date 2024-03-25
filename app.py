from flask import Flask, render_template, url_for, request, redirect, session,flash, jsonify
from werkzeug import exceptions as flaskExceptions
from flask_mail import Mail, Message, BadHeaderError
from flask_wtf import CSRFProtect
from argon2 import PasswordHasher, exceptions
import mysql.connector
from authlib.integrations.flask_client import OAuth
from authlib.integrations.base_client.errors import OAuthError
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from datetime import datetime, date, timedelta
from base64 import urlsafe_b64encode, urlsafe_b64decode
from binascii import Error as conversionError
from os import environ
from math import ceil
import forms

app = Flask(__name__)
oauth = OAuth(app)
#CSRF key for pages without WTForms
csrf = CSRFProtect(app)

app.config['SECRET_KEY'] = environ['FLASK_SECRET']
app.config['MAIL_SERVER'] = environ['MAIL_SERVER']
app.config['MAIL_PORT'] = environ['MAIL_PORT']
app.config['MAIL_USERNAME'] = environ['MAIL_USERNAME']
app.config['MAIL_PASSWORD'] = environ['MAIL_PASSWORD']
app.config['MAIL_USE_TLS'] = True
mailer = Mail(app)

#nitializing google authentication device flow (from google client secrets JSON file and additional data)
google_flow = Flow.from_client_secrets_file(
    'google_client_secret.json',
    scopes = 'openid',
    redirect_uri = 'http://127.0.0.1:5000/auth/google/callback'
)

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

#Creating a variable used to store all available courses from the database and pass them to the HTML template
courses = []
commonErrorMessage = 'Si è verificato un errore imprevisto. Per favore, riprova più tardi.'

@app.errorhandler(flaskExceptions.BadRequest)
def Error400(error):
    flash('Si è verificato un errore imprevisto durante la validazione del form. Per favore, riprova', 'Errore')
    return redirect(url_for('login'))

#Handler for `Error 404 Not Found`
@app.errorhandler(flaskExceptions.NotFound)
def pageNotFound(error):
    return redirect(url_for('index'))

@app.route('/')
def index():
    if not session.get('name'):
        return render_template('index.html')
    return redirect(url_for('userScreening'))

@app.route('/login', methods = ['GET', 'POST'])
def login():
    #Redirecting to user screening page if the user is already logged in
    if(session.get('name')):
        return redirect(url_for('userScreening'))
    form = forms.LoginForm()
    #Checking if form was submitted and all the form values and thr CSRF token are correct and valid in order to start login process
    if(form.validate_on_submit()):
        email = form.email.data
        pw = form.password.data
        
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
            flash("Account non trovato", 'Errore')
            return render_template('login.html', form = form)
        phasher = PasswordHasher()
        try:
            #Verifying the hashed password gotten from the database with the user input one in the form
            phasher.verify(response[0]['PW'], pw)
        #Non-matching passwords will throw `VerifyMismatchError`
        #Redirecting to login page form to retry the input
        except exceptions.VerifyMismatchError:
            #Sending an error message to back to the login page in order to display why the login didn't happen
            flash('La password non è corretta. Per favore, riprova', 'Errore')
            return render_template('login.html', form = form)
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
            session['googleConnected'] = bool(response[0]['googleID'])

            #Default last login value in database = fresh account so a new password needs to be set. Redirecting to password creation page
            if(session['lastLogin'] == 'Mai'):
                return redirect(url_for('updatePassword'))
            else:
                #Updating last login time and redirecting user to screening
                updateLastLoginTime()
                return redirect(url_for('userScreening'))
        finally:
            connection.close()
    return(render_template('login.html', form = form))

@app.route('/forgot-password', methods = ['GET', 'POST'])
def forgotPassword():
    #TODO: Add db field in `Credenziali` called = `passwordDimenticata` with `False` as default value
    form = forms.ResetPasswordForm()
    #If the form has not been submitted, the first redirect will be to the form for inputting the user's email, otherwise proceeding with user verification
    if(form.validate_on_submit()):
        email = form.email.data
        #Checking if the user exist by getting its relative userID from the database
        uid = verifyUserExistence(email)
        flash('Riceverai a breve un\'Email all\'indirizzo fornito se è registrato.', 'Successo')
        if(uid):
            #Getting the dictionary's `userID` key's value and parsing it to string
            uid = str(uid['userID'])
            message = Message(subject = 'Recupera Password',
                            recipients = [email],
                            html = render_template('recoverPasswordTemplate.html', userMail = b64_encode_decode(email).decode(), userID = b64_encode_decode(uid).decode()),
                            sender = ('Attendance Tracker Mailing System', environ['MAIL_USERNAME'])
                            )
            try:
                mailer.send(message)
            #Avoiding HTTP Header injections
            except BadHeaderError:
                flash('Si è verificato un errore durante l\'invio dell\'Email. Per favore più tardi', 'Errore')
        return redirect(url_for('login'))
    else:
        return render_template('reset-password-form.html',
                                form = form)

@app.route('/user/updatepassword', methods = ['GET', 'POST'])
def updatePassword():
    '''Lets the user update his freshly created account's password'''
    form = forms.UpdateResetPasswordForm()
    #Getting the needed values from the URL (params passed as GET values)
    userEmail = request.args.get('mail')
    userID = request.args.get('uid')
    #Processing form data and updating user password
    if(form.validate_on_submit()):
        newPassword = form.password.data
        connection = connectToDB()
        if(not connection):
            return redirect(url_for('index'))
        cursor = connection.cursor()
        #Getting the current password from the user
        cursor.execute('select PW from Credenziali\
                        where userID = %(uid)s',
                        {
                            'uid': session['uid']
                        }
                    )
        response = getValuesFromQuery(cursor)
        pHasher = PasswordHasher()
        try:
            pHasher.verify(str(response[0]['PW']), newPassword)
        #New and old passwords must be different, so the error must be triggered when `verifyMismatchError` is not raised
        except exceptions.VerifyMismatchError:
            pass
        else:
            flash("La password non può essere uguale a quella precedente. Per favore, riprova", 'Errore')
            return render_template('updatePassword.html',
                                    form = form)
        #Encoding the form obtained password and udpating the database
        hashedPW = pHasher.hash(newPassword.encode())
        cursor.execute("update Credenziali set PW = %(newPW)s\
                        where userID = %(uid)s",
                        {
                            'newPW': hashedPW,
                            'uid': session['uid']
                        }
                    )
        connection.commit()
        connection.close()
        session['lastLogin'] = updateLastLoginTime()
        flash('Password aggiornata con successo.', 'Successo')
        return redirect(url_for('login'))
    #Printing error message in case the form was submitted but the values were not valid
    elif(form.errors):
        flash('I campi inseriti non sono validi. Per favore, riprova', 'Errore')
        return render_template('updatePassword.html',
                                form = form)
    #Checking if the two needed parameters contain a value, otherwise redirecting to login page with an error message
    elif(userEmail and userID):
        #Decoding the URL obtained values from `Base64` to `String`
        userEmail = b64_encode_decode(userEmail, False)
        userID = b64_encode_decode(userID, False)
        #Managing conversion error with redirect to login page if `b64_encode_decode` function returns `False`
        if(not userEmail or not userID):
            flash(commonErrorMessage, 'Errore')
            return redirect(url_for('login'))
        #Query `count` result = 1 means account found so redirecting to update password form
        if(verifyUserExistence(userEmail, userID)['result'] == 1):
            session['uid'] = userID
            return render_template('updatePassword.html',
                                    form = form)
        else:
            flash('Questo utente non esiste.', 'Errore')
            return redirect(url_for('login'))
    #Rendering update password form if it's the first time logging in
    elif(session.get('name')):
        return render_template('updatePassword.html',
                                form = form)
    #Redirecting to login page with a generic error message if none of the conditions above are satisfied
    flash(commonErrorMessage, 'Errore')
    return redirect(url_for('login'))

@app.route('/auth/github')
def githubAuth():
    #NOTE: `_external` means that it's pointing to an external domain
    return oauth.github.authorize_redirect(url_for('authorize', _external = True, login = [login]))

@app.route('/auth/google')
def googleAuth():
    #Calling Google's OAuth authorization URL for managing developer console app and redirecting to callback page
    google_auth_uri = google_flow.authorization_url()
    return redirect(google_auth_uri[0])

@app.route('/auth/github/callback')
def authorize():
    #Getting the user values and starting the OAuth autorization process
    try:
        oauth.github.authorize_access_token()
        profile = oauth.github.get('user').json()
    except OAuthError:
        flash('Tentativo di collegamento fallito.', 'Errore')
        return redirect(url_for('login'))
    #`not login` = `False` means that the service requested is github account link (account already linked)
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
    #Requested login with github account
    else:
        #Account found, so redirecting to user screening page
        if(loginWithGithub(profile['id'])):
            return redirect(url_for('userScreening'))
        #Redirecting to login page if the account was not found
        flash("Nessun utente collegato a questo account Github.", 'Errore')
        return redirect(url_for('login'))

@app.route('/auth/google/callback', methods = ['GET'])
def googleAuthorization():
    #Managing denied google OAuth authorization
    if(request.args.get('error')):
        flash('Accesso con Google rifiutato. Per favore, riprova.', 'Errore')
        return redirect(url_for('login'))
    code = request.args.get('code')
    #Obtaining access token from google API in order to execute all user related requests
    google_flow.fetch_token(code = code)
    #Creating a resource variable to talk to google's API and obtain all needed data
    google_user_info = build('oauth2', 'v2', credentials = google_flow.credentials)
    #Asking google's API for user data (returned values `id` and `picture`)
    user_info = google_user_info.userinfo().get().execute()
    if(session.get('name')):
        #`checkUserGoogleConnection = False` means no user is using that Google account
        if(not checkUserGoogleConnection()):
            if(linkGoogleAccount(user_info['id'])):
                flash('Account Google collegato con successo', 'Successo')
            else:    
                flash('Questo account Google è già utilizzato da un altro utente.', 'Errore')
        return redirect(url_for('userScreening'))
    else:
        if(loginWithGoogle(user_info['id'])):
            return redirect(url_for('userScreening'))
        else:
            flash('Account non trovato.', 'Errore')
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
        flash('Account Github scollegato con successo.', 'Successo')
    return redirect(url_for('userScreening'))

@app.route('/auth/google/disconnect')
def unlinkGoogleAccount():
    #Checks if the logged user has a linked github account
    if(session.get('googleConnected')):
        connection = connectToDB()
        if(not connection):
            return redirect(url_for('index'))
        cursor = connection.cursor()
        cursor.execute('update Credenziali set googleID = NULL\
                    where userID = %(uid)s', {'uid': session['uid']})
        connection.commit()
        connection.close()
        session['googleConnected'] = False
        flash('Account Google disconnesso con successo.', 'Successo')
    return redirect(url_for('userScreening'))

@app.route('/user')
def userScreening():
    if(session.get('name')):
        #Redirecting to update password page if it's the first login
        if(session.get('lastLogin') == 'Mai'):
            return redirect(url_for('updatePassword'))
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
        #Managing indexError (returning valuef rom `getLessonsList` is a list, so that would be impossible to obtain the `0` index value if it's empty)
        try:
            #Getting the first lesson data only
            scheduledLessons = getLessonsList()[0][0]
        except IndexError:
            scheduledLessons = None
        return render_template('userScreening.html',
                            session = session,
                            helloMessage = getCustomMessage(),
                            scheduledLessons = scheduledLessons,
                        )
    else:
        flash('Devi prima fare il login.', 'Errore')
        return redirect(url_for('login'))

@app.route('/user/create', methods = ['GET', 'POST'])
def createUser():
    if(session.get('role') == 'Admin'):
        form = forms.UserCreationForm()
        #Updating courses list
        getCourses()
        if(form.validate_on_submit()):
            fname = form.fname.data.strip().capitalize()
            lname = form.lname.data.strip().capitalize()
            email = form.email.data.strip().lower()
            pw = form.password.data
            role = form.role.data
            chosenCourses = request.form.getlist('course')

            coursesNames = []
            coursesYears = []
            #Getting all checked courses names and years
            for course in chosenCourses:
                coursesYears.append(course.split("a ")[0])
                coursesNames.append(course.split("a ")[1])
            #Validating the chosen courses
            if(validateCoursesSelection(coursesNames, coursesYears)):
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
                        cursor.execute(*query)
                        #Sending request to DB
                        connection.commit()
                    cursor.execute('select max(userID) as "userID" from Utente')
                    userID = getValuesFromQuery(cursor)[0]['userID']
                    response = None
                    for x in range(len(coursesNames)):
                        cursor.execute('insert into Registrazione(userID, idCorso)\
                                        values(%(uid)s, (select idCorso from Corso where nomeCorso = %(courseName)s and annoCorso = %(courseYear)s))',
                                        {
                                            'uid': userID,
                                            'courseName': coursesNames[x],
                                            'courseYear': coursesYears[x]
                                        }
                                    )
                        connection.commit()
                        #Getting all upcoming lesson codes for every user course in order to automatically add a default row in the `Partecipazione` table
                        cursor.execute('select idLezione\
                                        from Lezione\
                                        inner join Corso on Corso.idCorso = Lezione.idCorso\
                                        where dataLezione >= %(dateToday)s\
                                        and nomeCorso = %(selectedCName)s\
                                        and annoCorso = %(selectedCYear)s',
                                        {
                                            'dateToday': date.today(),
                                            'selectedCName': coursesNames[x],
                                            'selectedCYear': coursesYears[x]
                                        }
                                    )
                        response = getValuesFromQuery(cursor)
                        for lesson in response:
                            #Adding the user to all lessons
                            cursor.execute('insert into Partecipazione(userID, idLezione)\
                                            values(%(uid)s, %(lessonID)s)',
                                            {
                                                'uid': userID,
                                                'lessonID': lesson['idLezione']
                                            }
                                        )
                            connection.commit()
                    flash('Account creato con successo.', 'Successo')
            #Redirecting back to register page if the input values are not correct
                else:
                    flash('Utente con questa Email già esistente', 'Errore')
                connection.close()
            else:
                flash('Devi selezionare una tipologia valida dal menu e almeno un corso dalla lista.', 'Errore')
        elif(form.errors):
            flash('I campi inseriti non sono validi. Per favore, riprova', 'Errore')
        return render_template('createUserForm.html',
                                form = form,
                                courses = courses)
    else:
        flash(commonErrorMessage, 'Errore')
        return(redirect(url_for('userScreening')))

@app.route('/lesson/create', methods = ['GET', 'POST'])
def createLesson():
    if(session.get('role') in ['Insegnante', 'Admin']):
        form = forms.LessonCreationForm_Admin()
        enrolledCourses = None
        #Getting user enrolled courses if the role is `Insegnante` in order to output as selection only his own courses and not the whole list
        if(session.get('role') == 'Insegnante'):
            form = forms.LessonCreationForm_Teacher()
            enrolledCourses = getUserEnrolledCourses()
            #Returned value = `False` means that the connection to the database failed
            if enrolledCourses is False:
                return redirect(url_for('index'))
            form.course.choices = [(course, course) for course in enrolledCourses]
        else:
            #Getting all teachers list and appending all the elements as tuples in the list
            teachersList = getTeachersList()
            form.assignedTeacher.choices[1:] = [(teacher['id'], teacher['Nome']) for teacher in teachersList]
        if(form.validate_on_submit()):
            subject = form.subject.data
            description = form.description.data
            lessonDate = form.lessonDate.data
            lessonStartTime = form.lessonStartTime.data
            lessonEndTime = form.lessonEndTime.data
            lessonRoom = form.room.data
            assignedTeacher = form.assignedTeacher.data if session['role'] == 'Admin' else session['uid']
            lessonType = request.form.get('lessonType')
            chosenCourseYear, chosenCourseName = form.course.data.split('a ')
            #Validating course selection with additional filter for enrolled courses (based on selected assigned teacher userID)
            if(validateCoursesSelection([chosenCourseName], [chosenCourseYear], assignedTeacher)):
                #Checking if the textboxes contain a valid value and the date to be higher or equal than today (cannot create a lesson on dates before current date)
                connection = connectToDB()
                cursor = connection.cursor()
                try:
                    cursor.execute('insert into Lezione(Materia, Descrizione, dataLezione, oraInizio, oraFine, Aula, Tipologia, idCorso, idInsegnante)\
                                    values (%(subjectName)s, %(description)s, %(lessonDate)s, %(lessonStartTime)s, %(lessonEndTime)s, %(lessonRoom)s, %(lessonType)s, (select idCorso from Corso where nomeCorso = %(courseName)s and annoCorso = %(courseYear)s), %(teacherID)s)',
                                    {
                                        'subjectName': subject.strip().capitalize(),
                                        'description': description.strip(),
                                        'lessonDate': lessonDate,
                                        'lessonStartTime': lessonStartTime,
                                        'lessonEndTime': lessonEndTime,
                                        'lessonRoom': lessonRoom.upper(),
                                        'lessonType': lessonType,
                                        'courseName': chosenCourseName,
                                        'courseYear': chosenCourseYear,
                                        'teacherID': assignedTeacher
                                    }
                                )
                    connection.commit()
                except mysql.connector.IntegrityError:
                    flash('I campi inseriti non sono validi. Per favore, riprova', 'Errore')
                    connection.close()
                    return render_template('createLessonForm.html',
                                            form = form)
                #Getting all users attending the lesson's course and adding them all to the `Partecipazione` table with default `Presenza` value (`0` or `False`)
                usersList = selectUsersFromCourse(chosenCourseName, chosenCourseYear)
                cursor.execute('select max(idLezione) from Lezione')
                latestLesson = cursor.fetchone()[0]
                #Adding all students and the assigned teacher to the `Partecipazione` table
                for user in usersList:
                    #Checking if the iterated user role is "Studente" or if the UID matches the selected lesson's assigned teacher id before adding the row
                    if(user['Tipologia'] == 'Studente' or user['userID'] == int(assignedTeacher)):
                        cursor.execute('insert into Partecipazione(userID, idLezione) values(%(uid)s, %(latestLessonID)s)',
                                        {
                                            'uid': user['userID'],
                                            'latestLessonID': latestLesson
                                        }
                                    )
                        connection.commit()
                connection.close()
                flash('Lezione creata con successo.', 'Successo')
            else:
                flash('Corso non trovato per l\'insegnante selezionato. Per favore, riprova', 'Errore')
        elif(form.errors):
            flash('I campi inseriti non sono validi. Per favore, riprova', 'Errore')
        return render_template('createLessonForm.html',
                                form = form)
    else:
        flash(commonErrorMessage, 'Errore')
        return redirect(url_for('userScreening'))

@app.route('/lesson/list', methods = ['GET'])
def lessonsList():
    if(session.get('name')):
        page = validatePageInput()
        if not page:
            return redirect(url_for('lessonsList', page = 1))
        #Showing 10 elements per page
        scheduledLessons, totalLessons = getLessonsList(10, page)
        #Calculating the total number of pages based on the total number of lessons
        totalPages = ceil(totalLessons / 10)
        #Redirecting to last page if the chosen page contains no lessons (e.g. empty list)
        if not scheduledLessons:
            return redirect(url_for('lessonsList', page = totalPages))
        return render_template('lessons.html',
                                scheduledLessons = scheduledLessons,
                                today = date.today().strftime('%d/%m/%Y'),
                                page = page,
                                totalPages = totalPages
                            )
    flash('Devi prima fare il login.', 'Errore')
    return redirect(url_for('login'))

@app.route('/lesson', methods = ['GET', 'POST'])
def manageLesson():
    if(session.get('role') in ['Admin', 'Insegnante']):
        try:
            #Getting the lesson id value from the  lessons list as `POST` and from the register attendances function as `GET`
            lessonID = int(request.values.get('id'))
        except (ValueError, TypeError):
            flash('Lezione non trovata.', 'Errore')
            return redirect(url_for('lessonsList'))
        connection = connectToDB()
        if not connection:
            return redirect(url_for('index'))
        cursor = connection.cursor()
        buttonAction = request.form.get('submitButton')
        #Checking the user required action and removing the selected lesson from the database if the submit button's value is `Remove`
        #TODO: Check for user role before removing (must me "Admin")
        if(buttonAction == 'Remove'):
            cursor.execute('delete from Lezione where idLezione = %(lessonID)s', {'lessonID': lessonID})
            connection.commit()
            flash('Lezione eliminata con successo.', 'Successo')
            return redirect(url_for('lessonsList'))
        elif(buttonAction == 'Edit'):
            form = forms.LessonUpdateForm_Admin() if session['role'] == 'Admin' else forms.LessonUpdateForm_Teacher()
            #Obtaining all lesosn's information and assigned teacher's enrolled courses in order to fill all select form fields
            lessonInfo = getLessonInfo(lessonID)
            enrolledCourses = getUserEnrolledCourses(lessonInfo['idInsegnante'])
            #Adding form select options based on teachers list and lesson's assigned teacher's enrolled courses
            form.course.choices[1:] = [(course, course) for course in enrolledCourses]
            #Setting a default value to the `teachersList`'s variable in order to not trigger the `UnboundLocalError` due to variable not declared
            teachersList = 1
            #Setting choices and default selected value for lesson's assigned teacher select form field if user role is "Admin"
            if(session['role'] == 'Admin'):
                teachersList = getTeachersList()
                form.assignedTeacher.choices[1:] = [(teacher['id'], teacher['Nome']) for teacher in teachersList]
            #Calling lesson data update function if the form fields are valid, otherwise rendering the form with the default values
            if(form.validate()):
                update_lesson_data(form)
                return redirect(url_for('lessonsList'))
            else:
                #Setting choices and default selected value for lesson's assigned teacher select form field if user role is "Admin"
                if(session['role'] == 'Admin'):
                    #NOTE: use `process_data` on SelectField to pre-select option if `choices` is dynamic
                    form.assignedTeacher.process_data(lessonInfo['idInsegnante'])
                #Redirecting to index page in case of failed connection to DB
                if not lessonInfo or not teachersList:
                    return redirect(url_for('index'))
                #Setting all lesson's values as autocompiled form field values
                form.subject.data = lessonInfo['Materia']
                form.description.data = lessonInfo['Descrizione']
                form.lessonDate.data = lessonInfo['dataLezione']
                form.lessonStartTime.data = timedeltaConverter(lessonInfo['oraInizio'], '%H:%M:%S')
                form.lessonEndTime.data = timedeltaConverter(lessonInfo['oraFine'], '%H:%M:%S')
                form.room.data = lessonInfo['aula']
                form.lessonType.data = lessonInfo['Tipologia']
                form.course.process_data(lessonInfo['nomeCorso'])
                form.lessonID.data = lessonInfo['idLezione']
            return render_template('lessonInfo.html',
                                    form = form,
                                    session = session)
        #Proceeding with entering the lesson management page if the user clicked on the `Manage` button
        else:
            #Validating lesson (can only select same date lessons)
            cursor.execute('select dataLezione from Lezione where idLezione = %(lessonID)s', {'lessonID': lessonID})
            #Managing possible `NoneType` if the lesson gets suddenly removed
            try:
                response = cursor.fetchone()[0]
            except TypeError:
                flash('Lezione non trovata.', 'Errore')
                return redirect(url_for('userScreening'))
            if(response != date.today()):
                return redirect(url_for('userScreening'))
            cursor.execute('select Utente.userID, Nome, Cognome, Materia, dataLezione, Lezione.idLezione, Presenza\
                            from Utente\
                            inner join Partecipazione on Utente.userID = Partecipazione.userID\
                            inner join Lezione on Partecipazione.idLezione = Lezione.idLezione\
                            where Utente.Tipologia = "Studente"\
                            and Lezione.idLezione = %(lessonID)s', {'lessonID': lessonID})
            response = getValuesFromQuery(cursor)
            if(not response):
                flash('Nessuno studente trovato per la lezione selezionata.', 'Errore')
                return redirect(url_for('lessonsList'))
            #Converting all gotten dates to a more user friendly format
            for lessonDate in response:
                lessonDate['dataLezione'] = lessonDate['dataLezione'].strftime('%d/%m/%Y')
            #Updating teacher attendance
            if(session['role'] == 'Insegnante'):
                cursor.execute('update Partecipazione set Presenza = 1\
                                where idLezione = %(lessonID)s\
                                and userID = %(uid)s', {'lessonID': lessonID, 'uid': session['uid']})
                connection.commit()
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
        flash('Presenze registrate con successo.', 'Successo')
    return redirect(url_for('manageLesson', id = selectedLessonID))

@app.route('/lesson/attendances', methods = ['GET'])
def getAttendancesCount():
    '''API that returns the list of all attended courses attendances count'''
    try:
        return getLessonsAttendancesCount(int(request.args.get('range')))
    except ValueError:
        return getLessonsAttendancesCount()

@app.route('/lesson/attendances/percentage', methods = ['GET'])
def getAttendancesPercentage():
    '''API that returns the total number of lessons and the total count of attendances'''
    connection = connectToDB()
    if not connection:
        return []
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

@app.route('/course/create', methods = ['GET', 'POST'])
def create_course():
    if(session.get('role') == 'Admin'):
        form = forms.CourseCreationForm()
        if(form.validate_on_submit()):
            courseName = form.courseName.data
            courseYear = form.courseYear.data
            connection = connectToDB()
            if(not connection):
                return redirect(url_for('index'))
            cursor = connection.cursor()
            try:
                cursor.execute('insert into Corso(nomeCorso, annoCorso) values(%(courseName)s, %(courseYear)s)', {'courseName': courseName.strip().capitalize(), 'courseYear': courseYear})
                connection.commit()
            #Managing unique constraint SQL error
            except mysql.connector.IntegrityError:
                flash('Questo corso è già esistente.', 'Errore')
            else:
                flash('Corso creato con successo.', 'Successo')
            finally:
                connection.close()
        #Alternative error message printout if the input values are not valid
        elif(form.errors):
            flash('I campi inseriti non sono validi. Per favore, riprova', 'Errore')
        return render_template('createCourseForm.html', form = form)
    else:
        flash(commonErrorMessage, 'Errore')
        return redirect(url_for('userScreening'))

@app.route('/user/list', methods = ['GET'])
def usersList():
    if(session.get('role') == 'Admin'):
        #Validating the page value passed as GET parameter and redirecting with the correct page value if needed
        page = validatePageInput()
        if not page:
            return redirect(url_for('usersList', page = 1))
        #Calculating the total number of pages based on the total number of lessons
        usersList, totalUsers = getUsersList(10, page)
        totalPages = ceil(totalUsers / 10)
        #Redirecting to last page if the chosen page contains no lessons (e.g. empty list)
        if not usersList:
            return redirect(url_for('usersList', page = totalPages))
        return render_template('usersList.html',
                                users = usersList,
                                page = page,
                                totalPages = totalPages
                            )
    return redirect(url_for('userScreening'))

@app.route('/user/select', methods = ['GET', 'POST'])
def select_user():
    uid = request.values.get('userID')
    #Loading update user data as administrator
    if(session.get('role') == 'Admin' and uid):
        if(request.form.get('action') == 'Edit'):
            if(uid):
                form = forms.UserUpdateForm()
                if(form.validate()):
                    update_user_data(form, uid)
                    return redirect(url_for('usersList'))
                selectedUser = getUserData(uid)
                getCourses()
                enrolledCourses = getUserEnrolledCourses(uid)
                form.fname.data = selectedUser['Nome']
                form.lname.data = selectedUser['Cognome']
                form.email.data = selectedUser['Email']
                form.role.data = selectedUser['Tipologia']
                return render_template('userInfo.html',
                                        uid = uid,
                                        form = form,
                                        courses = courses,
                                        enrolledCourses = enrolledCourses)
        elif(request.form.get('action') == 'Remove'):
            deleteUser(uid)
            flash('Utente rimosso con successo.', 'Successo')
            return redirect(url_for('usersList'))
    #Loading update self email & password information
    elif(session.get('name')):
        form = forms.UserUpdateForm_Standard()
        selectedUser = getUserData(session['uid'])['Email']
        if(form.validate()):
            update_user_data(form)
        #Outputting possible password field input errors
        elif(form.password_verify.errors):
            flash('I campi inseriti non sono validi. Per favore, riprova', 'Errore')
            return render_template('userInfo.html',
                                    form = form)
        else:
            form.email.data = selectedUser
            return render_template('userInfo.html',
                                    form = form)
    return redirect(url_for('userScreening'))

# @app.route('/user/update', methods = ['GET', 'POST'])
def update_user_data(form, uid = None):
    #`not request.form.get('uid')` means that the administrator wants to update his own data
    #NOTE: (`uid` is a special field in `userInfo.html` form which links the selected user id to the button value with name `uid`)
    if(session.get('role') in ['Studente', 'Insegnante'] or not uid):
        if(updateDataAsUser(form)):
            flash('Utente modificato con successo.', 'Successo')
            return True
        else:
            return False
    elif(session.get('role') == 'Admin'):
        return updateDataAsAdmin(uid, form)
    else:
        flash(commonErrorMessage, 'Errore')
        return False

@app.route('/user/courses', methods = ['GET'])
def userEnrolledCourses():
    '''API returning a list of all selected teacher's enrolled courses\n
    Takes as parameter the teacher's user id'''
    selectedUserID = request.args.get('uid')
    return jsonify(getUserEnrolledCourses(selectedUserID))

@app.route('/user/logout')
def logout():
    #Checking if session exists before clearing it
    if(session.get('name')):
        updateLastLoginTime()
        session.clear()
        flash("Logout effettuato con successo.", 'Successo')
    return redirect(url_for('login'))

@app.route('/cookie-policy')
def informationPage():
    return render_template('cookiePolicy.html')

@app.route('/terms-and-conditions')
def termsPage():
    return render_template('termsAndConditions.html')

@app.route('/privacy')
def privacyPage():
    return render_template('privacyPolicy.html')


def connectToDB():
    '''Starts a connection to the database with the given data'''
    try:
        connection = mysql.connector.connect(user = environ['DB_USERNAME'], password = environ['DB_PWORD'], host = environ['DB_HOSTNAME'], database = environ['DB_NAME'])
    except mysql.connector.Error:
        flash('Il sistema sta avendo dei problemi sconosciuti al momento. Per favore riprova più tardi', 'Errore')
        return False
    return connection

def getCourses():
    '''Gets all courses from database'''
    global courses
    courses = []
    connection = connectToDB()
    if(not connection):
        return redirect(url_for('index'))
    cursor = connection.cursor()
    cursor.execute("select nomeCorso, annoCorso from Corso")
    #Overwriting list with newly values from DB response
    response = getValuesFromQuery(cursor)
    for course in response:
        courses.append(f"{course['annoCorso']}a {course['nomeCorso']}")



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
    '''Programmatically updates user's last login time on database.\n
    Value update is based on `session['uid']` value'''
    connection = connectToDB()
    if(not connection):
        return redirect(url_for('index'))
    cursor = connection.cursor()
    cursor.execute("update Utente set ultimoLogin = %(timeNow)s\
                    where userID = %(uid)s",
                    {
                        'timeNow': datetime.now().strftime('%d/%m/%Y %H:%M'),
                        'uid': session['uid']
                    }
                )
    connection.commit()
    cursor.close()
    connection.close()
    #Returning formatted date to be used for a better value output
    return date.today().strftime('%d/%m/%Y').replace(' ', ' alle ')

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
    #`response = None` means that the defined google account ID is already linked to a different account
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
    cursor.execute("select Utente.userID, Nome, Tipologia, ultimoLogin, Credenziali.githubID, Credenziali.googleID\
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
        session['googleConnected'] = True if response[0]['googleID'] else False
        accountFound = True
    #Returning `False` if the github user ID was not found in the table
    else:
        accountFound = False
    connection.close()
    return accountFound

def checkUserGoogleConnection():
    '''Checks if the user has a linked Google account'''
    connection = connectToDB()
    if(not connection):
        return redirect(url_for('index'))
    cursor = connection.cursor()
    response = cursor.execute('select googleID from Credenziali where userID = %(uid)s', {'uid': session['uid']})
    returnedValue = bool(response)
    connection.close()
    return returnedValue

def linkGoogleAccount(userID):
    connection = connectToDB()
    if(not connection):
        return redirect(url_for('index'))
    cursor = connection.cursor()
    #Checking if the github user ID is already in the database (same UID cannot be used my more than 1 person)
    cursor.execute('select googleID from Credenziali where googleID = %(google_userID)s', {'google_userID': userID})
    response = cursor.fetchone()
    #`response = None` means that the defined google account ID is already linked to a different account
    if(response != None):
        accountLinked = False
    else:
        #Updating table column with github user id
        cursor.execute("update Credenziali set googleID = %(google_userID)s where userID = %(uid)s", {'google_userID': userID, 'uid': session['uid']})
        connection.commit()
        session['googleConnected'] = True
        accountLinked = True
    connection.close()
    return accountLinked

def loginWithGoogle(googleID):
    '''Lets the user login with a valid linked github account'''
    connection = connectToDB()
    if(not connection):
        return redirect(url_for('index'))
    cursor = connection.cursor()
    #Finding between all `Utente`'s table columns for a matching github user ID and storing its relative data in a session
    cursor.execute("select Utente.userID, Nome, Tipologia, ultimoLogin, Credenziali.githubID, Credenziali.googleID\
                    from Utente\
                    inner join Credenziali on Utente.userID = Credenziali.userID\
                    where googleID = %(google_userID)s", {'google_userID': str(googleID)})
    response = getValuesFromQuery(cursor)
    #Checking for `response` var content in case the Query returns no columns so returned value = empty list
    if(response and response[0]['googleID'] == str(googleID)):
        session['uid'] = response[0]['userID']
        session['name'] = response[0]['Nome']
        session['role'] = response[0]['Tipologia']
        #Reformatting last login date for clean output
        session['lastLogin'] = response[0]['ultimoLogin'].replace(' ', ' alle ')
        session['googleConnected'] = True
        session['githubConnected'] = True if response[0]['githubID'] else False
        accountFound = True
    #Returning `False` if the github user ID was not found in the table
    else:
        accountFound = False
    connection.close()
    return accountFound

def getUsersList(limit = None, page = 1):
    '''Obtains all users from the database and returns a matrix'''
    connection = connectToDB()
    if(not connection):
        return redirect(url_for('index'))
    cursor = connection.cursor()
    cursor.execute("select Utente.userID, Nome, Cognome, Tipologia, nomeCorso, annoCorso\
                    from Utente\
                    left join Registrazione on Utente.userID = Registrazione.userID\
                    left join Corso on Registrazione.idCorso = Corso.idCorso\
                    group by(userID)\
                    order by case\
                        when Tipologia = 'Admin' then 1\
                        when Tipologia = 'Insegnante' then 2\
                        when Tipologia = 'Studente' then 3\
                    end")
    usersList = getValuesFromQuery(cursor)
    totalUsers = len(usersList)
    connection.close()
    if(limit):
        endLimit = limit * page
        startLimit = endLimit - limit
        #Modelling the list in order to return only the needed range of lessons
        usersList = usersList[startLimit:endLimit]
    return [usersList, totalUsers]

def getUserData(uid):
    connection = connectToDB()
    if(not connection):
        return redirect(url_for('index'))
    cursor = connection.cursor()

    cursor.execute('select Utente.userID, Nome, Cognome, Tipologia, Email, nomeCorso, annoCorso\
                    from Utente\
                    left join Credenziali on Utente.userID = Credenziali.userID\
                    left join Registrazione on Registrazione.userID = Utente.userID\
                    left join Corso on Corso.idCorso = Registrazione.idCorso\
                    where Utente.userID = %(uid)s', {'uid': int(uid)})
    response = getValuesFromQuery(cursor)
    
    #Trying to format course name
    #If the `IndexError` gets triggered, the user has no enrolled courses so the return course name will be empty
    try:
        response[0]['nomeCorso'] = getUserCourses(response)
        response[0].pop('annoCorso')
    except IndexError:
        pass
    connection.close()
    return response[0]

def updateDataAsAdmin(userID, form):
    '''Shorthand function to update any user data as administrator'''
    fname = form.fname.data.strip().capitalize()
    lname = form.lname.data.strip().capitalize()
    email = form.email.data.strip().lower()
    pw = form.password.data
    hashedPW = ''
    role = form.role.data
    chosenCourses = request.form.getlist('course')
    
    userEnrolledCourses = getUserEnrolledCourses(userID)
    coursesNames = []
    coursesYears = []
    for course in chosenCourses:
        coursesYears.append(course.split("a ")[0])
        coursesNames.append(course.split("a ")[1])
    if(validateCoursesSelection(coursesNames, coursesYears)):
        #Checking if all the form fields input are not empty
        if(pw):
            phasher = PasswordHasher()
            hashedPW = phasher.hash(pw.encode())
        connection = connectToDB()
        if(not connection):
            return redirect(url_for('index'))
        #Creating a cursor reponsible for query executions
        cursor = connection.cursor()
        #Checking the user old role before modification in order to execute some additional role validation
        #e.g. Cannot update from "Insegnante" to "Studente"
        cursor.execute('select Tipologia\
                        from Utente\
                        where userID = %(uid)s',
                        {
                            'uid': userID
                        }
                    )
        oldUserRole = cursor.fetchone()[0]
        #Admin/Teacher to student conversion
        if(oldUserRole in ('Insegnante', 'Admin') and role == 'Studente'):
            #Removing teacher from all lessons in which the userID is mentioned
            if(oldUserRole == 'Insegnante'):
                cursor.execute('update Lezione\
                                set idInsegnante = NULL\
                                where idInsegnante = %(teacherID)s',
                                {
                                    'teacherID': userID
                                }
                            )
                connection.commit()
            #Getting all scheduled lessons for that user and inserting them all in the "Partecipazione" table with an initial "Presenza" value of `0`
            scheduledLessons = getLessonsList(uid = userID)[0]
            for lesson in scheduledLessons:
                cursor.execute('insert into Partecipazione(userID, idLezione)\
                                values(%(userID)s, %(lessonID)s)',
                                {
                                    'userID': userID,
                                    'lessonID': lesson['idLezione']
                                }
                            )
                connection.commit()
        #Student to Admin/Teacher conversion
        elif(oldUserRole == 'Studente' and role in ('Insegnante', 'Admin')):
            #Removing all scheduled lessons for dates above the current date
            cursor.execute('delete Partecipazione\
                            from Partecipazione\
                            inner join Lezione on Lezione.idLezione = Partecipazione.idLezione\
                            where dataLezione >= %(today)s\
                            and userID = %(userID)s',
                            {
                                'today': date.today(),
                                'userID': userID
                            }
                        )
            connection.commit()
        #Checking if the Email/UID combination returns no users (count result = 0) to prevent possible primary key duplicates error
        cursor.execute('select count(*)\
                        from Credenziali\
                        where Email = %(newEmail)s\
                        and userID != %(userID)s',
                        {
                            'newEmail': email,
                            'userID': userID
                        }
                    )
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
                cursor.execute(*query)
                connection.commit()
            for x in range(len(coursesNames)):
                #Adding the user to all the upcoming lessons of the new course (only if it's a "Studente")
                cursor.execute('select idCorso from Corso where nomeCorso = %(courseName)s and annoCorso = %(courseYear)s', {'courseName': coursesNames[x], 'courseYear': coursesYears[x]})
                courseID = cursor.fetchone()[0]
                #Making all attendanced manipulation operation only if the user role is "Studente"
                if(role == 'Studente'):
                    if(chosenCourses[x] not in userEnrolledCourses):
                        #Getting course id starting from course name and year (unique fields) and storing it in the `courseID` variable 
                        #Getting all upcoming lessons of the course
                        cursor.execute('select idLezione from Lezione\
                                        where dataLezione >= %(today)s\
                                        and idCorso = %(courseID)s', {'today': date.today(), 'courseID': courseID})
                        upcomingLessons = getValuesFromQuery(cursor)
                        #Adding the default attendance value for each one in the list
                        for lesson in upcomingLessons:
                            cursor.execute('insert into partecipazione(userID, idLezione)\
                                            values(%(uid)s, %(lessonID)s)',
                                            {
                                                'uid': userID,
                                                'lessonID': lesson['idLezione']
                                            }
                                        )
                            connection.commit()
                    try:
                        #Checking if an attended course was removed from the user
                        #If so, all the scheduled lessons will be removed from the user attendance
                        if(userEnrolledCourses[x] not in chosenCourses):
                            #Getting the enrolled course id which will be used for attendances removal in the "delete" query
                            cursor.execute('select idCorso from Corso where nomeCorso = %(courseName)s and annoCorso = %(courseYear)s', {'courseName': userEnrolledCourses[x].split('a ')[1], 'courseYear': userEnrolledCourses[x].split('a ')[0]})
                            enrolledCourseID = cursor.fetchone()[0]
                            #NOTE: Removing only the upcoming lessons in order to keep user lessons attendances history
                            cursor.execute('delete Partecipazione\
                                            from Partecipazione\
                                            inner join Lezione on Lezione.idLezione = Partecipazione.idLezione\
                                            where userID = %(userID)s\
                                            and idCorso = %(courseID)s\
                                            and dataLezione >= %(today)s',
                                            {
                                                'userID': userID,
                                                'courseID': enrolledCourseID,
                                                'today': date.today()
                                            }
                                        )
                            connection.commit()
                    #Managing `IndexError` error because the user enrolled courses list may be shorter than the chosen courses list (which is the subject of iteration)
                    except IndexError:
                        pass
                #Adding back all chosen courses to the "Registrazione" table
                cursor.execute('insert into Registrazione(userID, idCorso)\
                                values(%(uid)s, %(courseID)s)',
                                {
                                    'uid': userID,
                                    'courseID': courseID
                                }
                            )
                connection.commit()
            flash('Dati aggiornati con successo.', 'Successo')
        else:
            flash('Questo indirizzo Email è già associato a un altro account. Per favore, riprova.', 'Errore')
        #Closing connection
        connection.close()
    else:
        flash('Devi selezionare una tipologia valida dal menu e almeno un corso dalla lista.', 'Errore')
    return userID

def updateDataAsUser(form):
    email = form.email.data.strip().lower()
    pw = form.password.data
    hashedPW = ''
    queries = []
    
    connection = connectToDB()
    if(not connection):
        return redirect(url_for('index'))
    cursor = connection.cursor()
    #Checking if the Email/UID combination returns no users (count result = 0) to prevent possible primary key duplicates error
    cursor.execute('select count(*)\
                    from Credenziali\
                    where Email = %(newEmail)s\
                    and userID != %(uid)s',
                    {
                        'newEmail': email,
                        'uid': session['uid']
                    }
                )
    response = cursor.fetchone()
    if(response[0] == 1):
        flash('Questo indirizzo Email è già associato a un altro account. Per favore, riprova.', 'Errore')
        return False
    queries.append(['update Credenziali set Email = %(newEmail)s where userID = %(uid)s', {'newEmail': email, 'uid': session['uid']}])
    if(pw):
        phasher = PasswordHasher()
        hashedPW = phasher.hash(pw.encode())
        queries.append(['update Credenziali set PW = %(updatedHashedPW)s where userID = %(userID)s', {'updatedHashedPW': hashedPW, 'userID': session['uid']}])
    if(not queries):
        flash('Nessun dato fornito per la modifica. Per favore, riprova', 'Errore')
        return False
    for query in queries:
        cursor.execute(*query)
        connection.commit()
    connection.close()
    return True

def validateCoursesSelection(coursesNames, coursesYears, userFilter = None):
    '''Gets all courses names and relative years as parameters and executes a query for each item to check if the actual selection exists.\n
    Also allows to add an additional filter for the validation based on chosen userID to be checked (preference passed in `userFilter` function param)\n
    Returns `False` if the DB response returns `None`, else `True` if all requests return a value'''
    connection = connectToDB()
    if not connection:
        return False
    cursor = connection.cursor()
    preparedQuery = "select count(*)\
                    from Corso\
                    where nomeCorso = %(courseName)s and annoCorso = %(courseYear)s"
    if(userFilter):
        preparedQuery = "select count(*)\
                        from Corso\
                        inner join Registrazione on Registrazione.idCorso = Corso.idCorso\
                        where nomeCorso = %(courseName)s\
                        and annoCorso = %(courseYear)s\
                        and userID = %(uid)s"
    for course in range(len(coursesNames)):
        cursor.execute(preparedQuery, {'courseName': coursesNames[course], 'courseYear': coursesYears[course], 'uid': userFilter})
        if(cursor.fetchone()[0] == 0):
            return False
    return True

def getCustomMessage():
    '''Returns a custom message based on the system clock time to be printed out in the user screening page'''
    #Matrix with all the times ranges and the relative printout message
    timesRange = [[0,5, '🌙 Buonanotte'],[6,12, '👨‍🏫 Buongiorno'],[13,18, '📚 Buon pomeriggio'],[19,24, '☕️ Buona sera']]
    currentTime = int(datetime.now().strftime('%H'))
    #Iterating through all the list elements and checking the current time range location to obtain the right message
    for timeRange in timesRange:
        if(currentTime >= timeRange[0] and currentTime <= timeRange[1]):
            return timeRange[2]
        
def getUserCourses(response):
    '''Getting all courses from the query and creating a single list with all the obtained ones'''
    if not response:
        return response
    response[0]['nomeCorso'] = [f"{response[0]['annoCorso']}a {response[0]['nomeCorso']}"]
    for course in response[1:]:
        response[0]['nomeCorso'].append(f"{course['annoCorso']}a {course['nomeCorso']}")
    return response[0]['nomeCorso']

def deleteUser(uid):
    '''Removes a defined user from the database'''
    connection = connectToDB()
    cursor = connection.cursor()
    cursor.execute('delete from Utente where userID = %(uid)s', {'uid': uid})
    connection.commit()
    connection.close()

def getLessonsList(limit = None, page = 1, uid = None, isTeacher = False):
    '''Executes a query and returns all the upcoming lessons based on user type and enrolled courses filters and the total number of lessons\n
    Takes as parameters a `limit` variable used to limit the number of results and a `page` variable used to get the next `limit`ed results.\n
    Also allows to get the upcoming lessons of a determined user by passing the `uid` and `isTeacher` parameters which respectively represent the userID to get the values to and if the user is a Teacher, the `isTeacher` value must be set to `True`'''
    connection = connectToDB()
    if(not connection):
        return False
    cursor = connection.cursor()
    #Default query for all user types
    preparedQuery = [
        'select Lezione.idLezione, Materia, Descrizione, dataLezione, oraInizio, oraFine, aula, Tipologia, nomeCorso, annoCorso, Presenza\
        from Lezione\
        inner join Corso on Corso.idCorso = Lezione.idCorso\
        inner join Partecipazione on Partecipazione.idLezione = Lezione.idLezione\
        where dataLezione >= %(today)s', {'today': date.today()}
    ]
    #Adding course filter for students and teachers
    if(session.get('role') in ['Studente', 'Insegnante'] or uid):
        preparedQuery[0] += ' and Lezione.idCorso in (\
                                select idCorso\
                                from Registrazione\
                                inner join Utente on Utente.userID = Registrazione.userID\
                                where Utente.userID = %(userID)s\
                            )'
        preparedQuery[1].setdefault('userID', uid if uid else session['uid'])
    #Adding assigned lessons filter for teachers
    if(session.get('role') == 'Insegnante' or isTeacher):
        preparedQuery[0] += ' and idInsegnante = %(teacherID)s'
        preparedQuery[1].setdefault('teacherID', uid if isTeacher else session['uid'])
    #Adding the last SQL directives
    preparedQuery[0] += ' group by Lezione.idLezione\
                        order by dataLezione, Materia asc'
    #Executing the query in order to obtain the total number of lessons and their relative data and eventually modifying the list if it needs to be limited
    cursor.execute(*preparedQuery)
    response = getValuesFromQuery(cursor)
    totalLessons = len(response)
    #Calculating the starting and ending limit for SQL query and returning the data relative to selected page
    if(limit):
        endLimit = limit * page
        startLimit = endLimit - limit
        #Modelling the list in order to return only the needed range of lessons
        response = response[startLimit:endLimit]
    #Converting all gotten dates to a more user friendly format
    for lesson in response:
        lesson['dataLezione'] = lesson['dataLezione'].strftime('%d/%m/%Y')
        lesson['oraInizio'] = timedeltaConverter(lesson['oraInizio'], '%H:%M:%S').strftime('%H:%M')
        lesson['oraFine'] = timedeltaConverter(lesson['oraFine'], '%H:%M:%S').strftime('%H:%M')
        #Updating course name with course year and name combination and removing course year key from dict
        lesson['nomeCorso'] = f"{lesson['annoCorso']}a {lesson['nomeCorso']}"
        lesson.pop('annoCorso')
    connection.close()
    return [response, totalLessons]

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
    '''Takes a string as input parameter and returns its relative base64 encoded/decoded value\
        If `encode` parameter is `True`, the string will be encoded, if it's `False` it will be decoded'''
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
    '''Executes a query and returns the count of users attending a defined course\n
        Returns a list of dictionaries'''
    connection = connectToDB()
    cursor = connection.cursor()
    cursor.execute('select Utente.userID, Utente.Tipologia\
                    from Corso\
                    inner join Registrazione on Registrazione.idCorso = Corso.idCorso\
                    inner join Utente on Utente.userID = Registrazione.userID\
                    where nomeCorso = %(courseName)s and annoCorso = %(courseYear)s\
                    and Utente.Tipologia in ("Studente", "Insegnante")', {'courseName': courseName, 'courseYear': courseYear})
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
    if(session.get('role') == 'Insegnante'):
        preparedQuery[0] += ' and idInsegnante = %(teacherID)s'
        preparedQuery[1].setdefault('teacherID', session['uid'])
    #Adding the last SQL directives
    preparedQuery[0] += ' group by nomeCorso, dataLezione, Materia order by dataLezione'
    cursor.execute(*preparedQuery)
    jsonResponse = reformatResponse(getValuesFromQuery(cursor))
    return jsonify(jsonResponse)

def reformatResponse(response):
    '''Gets a list and converts each date to the desired format\
    Returns a list of dictionaries'''
    orderedResponse = []
    for col in response:
        orderedResponse.append({'nomeCorso': f"{col['annoCorso']}a {col['nomeCorso']}", 'dataLezione': col['dataLezione'].strftime('%d/%m/%Y'), 'conteggioPresenze': col['conteggioPresenze']})
    return orderedResponse

def getUserEnrolledCourses(uid = None):
    '''Executes a query and gets all courses names and years based on userID\n
        If `uid` parameter is not passed, the default value will be `session['uid']`\n
        Returns a list if the query returns valid values, else `False` if the connection to the database fails'''
    connection = connectToDB()
    if not connection:
        return False
    cursor = connection.cursor()
    cursor.execute('select nomeCorso, annoCorso\
                    from Corso\
                    inner join Registrazione on Corso.idCorso = Registrazione.idCorso\
                    inner join Utente on Registrazione.userID = Utente.userID\
                    where Utente.userID = %(uid)s', {'uid': uid if uid else session['uid']})
    response = getValuesFromQuery(cursor)
    responseList = []
    connection.close()
    for course in response:
        course['nomeCorso'] = f"{course['annoCorso']}a {course['nomeCorso']}"
        responseList.append(course['nomeCorso'])
    return responseList

def getTeachersList():
    '''Executes a query and returns a list of all teachers IDs, names and surnames'''
    connection = connectToDB()
    if not connection:
        return False
    cursor = connection.cursor()
    cursor.execute('select userID, Nome, Cognome from Utente where Tipologia = "Insegnante"')
    response = getValuesFromQuery(cursor)
    responseList = []
    for user in response:
        responseList.append({'id': user['userID'], 'Nome': f"{user['Nome']} {user['Cognome']}"})
    return responseList

def validatePageInput():
    '''Gets from the URL the `page` parameter and validates it based on some basic controls\n
    Returns `page` if the value is correct, otherwise `False` if it's not valid'''
    try:
        page = int(request.args.get('page')) or 1
    #Returning to page 1 if the page requedted in the URL is malformed (example chars instead of numbers or `page` param not provided in URL)
    except (ValueError, TypeError):
        return False
    #Correcting the `page` parameter if the input value is lower or equal than 0
    if(page <= 0):
        return False
    return page

def getLessonInfo(lessonID):
    connection = connectToDB()
    if not connection:
        return False
    cursor = connection.cursor()
    cursor.execute('select Lezione.idLezione, Materia, Descrizione, dataLezione, oraInizio, oraFine, aula, Lezione.Tipologia, idInsegnante, Nome, Cognome, nomeCorso, annoCorso\
                    from Lezione\
                    inner join Utente on Utente.userID = Lezione.idInsegnante\
                    inner join Corso on Corso.idCorso = Lezione.idCorso\
                    where Lezione.idLezione = %(lessonID)s',
                    {
                        'lessonID': lessonID
                    }
                )
    response = getValuesFromQuery(cursor)
    response[0]['Nome'] = f"{response[0]['Nome']} {response[0]['Cognome']}"
    response[0].pop('Cognome')
    response[0]['nomeCorso'] = f"{response[0]['annoCorso']}a {response[0]['nomeCorso']}"
    response[0].pop('annoCorso')
    connection.close()
    return response[0]

def update_lesson_data(form):
    '''Updates lesson's data based on form submitted and validated values\n
    Returns `True` if the process succeeds, otherwise `False` with a flashed message if the process catches an error'''
    if(session.get('role') in ['Admin', 'Insegnante']):
        #Obtaining all form's fields' values
        lessonID = form.lessonID.data
        subject = form.subject.data
        description = form.description.data
        lessonDate = form.lessonDate.data
        lessonStartTime = form.lessonStartTime.data
        lessonEndTime = form.lessonEndTime.data
        lessonRoom = form.room.data
        assignedTeacher = form.assignedTeacher.data if session['role'] == 'Admin' else session['uid']
        lessonType = form.lessonType.data
        chosenCourseYear, chosenCourseName = form.course.data.split('a ')
        #Validating course selection with additional filter for enrolled courses (based on selected assigned teacher userID)
        if(validateCoursesSelection([chosenCourseName], [chosenCourseYear], assignedTeacher)):
            #Checking if the textboxes contain a valid value and the date to be higher or equal than today (cannot create a lesson on dates before current date)
            connection = connectToDB()
            if not connection:
                return False
            cursor = connection.cursor()
            #Checking if the chosen leson still exists in the database (possible deletion in the meantime)
            cursor.execute('select count(*) from Lezione where idLezione = %(lessonID)s', {'lessonID': lessonID})
            if(not cursor.fetchone()[0]):
                flash('Nessuna lezione trovata.', 'Errore')
                return False
            lessonInfo = getLessonInfo(lessonID)
            #Checking if the chosen lesson's assigned teacher and/or chosen course is different than the previously defined one
            teacherChanged = int(assignedTeacher) != lessonInfo['idInsegnante']
            courseChanged = form.course.data != lessonInfo['nomeCorso']
            #Updating all lesson's data
            cursor.execute('update Lezione\
                            set Materia = %(subject)s,\
                            Descrizione = %(description)s,\
                            dataLezione = %(lessonDate)s,\
                            oraInizio = %(lessonStartTime)s,\
                            oraFine = %(lessonEndTime)s,\
                            aula = %(room)s,\
                            idInsegnante = %(teacherID)s,\
                            Tipologia = %(lessonType)s,\
                            idCorso = (select idCorso from Corso where nomeCorso = %(courseName)s and annoCorso = %(courseYear)s)\
                            where idLezione = %(lessonID)s',
                            {
                                'subject': subject.strip().capitalize(),
                                'description': description.strip().capitalize(),
                                'lessonDate': lessonDate,
                                'lessonStartTime': lessonStartTime,
                                'lessonEndTime': lessonEndTime,
                                'room': lessonRoom.upper(),
                                'teacherID': assignedTeacher,
                                'lessonType': lessonType,
                                'courseName': chosenCourseName, 
                                'courseYear': chosenCourseYear,
                                'lessonID': lessonID
                            }
                        )
            connection.commit()
            #Updating the lesson's attendance field in the `Partecipazione` DB table if the `teacherChanged` value is `True`
            if(teacherChanged):
                #Removing the previous teacher's attendance value at first
                cursor.execute('delete Partecipazione\
                                from Partecipazione\
                                inner join Utente on Utente.userID = Partecipazione.userID\
                                where idLezione = %(lessonID)s\
                                and Tipologia = "Insegnante"',
                                {
                                    'lessonID': lessonID
                                }
                            )
                connection.commit()
                #Then inserting the newest row in the table
                cursor.execute('insert into Partecipazione(userID, idLezione) values(%(teacherID)s, %(lessonID)s)', {'teacherID': assignedTeacher, 'lessonID': lessonID})
                connection.commit()
            #Updating students' attendance field in the `Partecipazione` DB table if the lesson's course has changed
            if(courseChanged):
                cursor.execute('delete Partecipazione\
                                from Partecipazione\
                                inner join Utente on Utente.userID = Partecipazione.userID\
                                where idLezione = %(lessonID)s\
                                and Tipologia = "Studente"',
                                {
                                    'lessonID': lessonID
                                }
                            )
                connection.commit()
                studentsList = selectUsersFromCourse(chosenCourseName, chosenCourseYear)
                for student in studentsList:
                    #Filtering for students user role only
                    if(student['Tipologia'] == 'Studente'):
                        cursor.execute('insert into Partecipazione(userID, idLezione)\
                                        values(%(studentID)s, %(lessonID)s)',
                                        {
                                            'studentID': student['userID'],
                                            'lessonID': lessonID
                                        }
                                    )
                        connection.commit()
            flash('Lezione modificata con successo.', 'Successo')
        #NOTE: Error message in case the form's input values are not in the expexted array of possible values
        else:
            flash('Devi selezionare una tipologia di lezione e un corso valido.', 'Errore')
            return False
        connection.close()
        return True
    return False

def timedeltaConverter(time, timeFormat):
    '''Converts a given `timedelta` type to datetime\n
    Takes as parameters the actual `time` and the format in order to correctly convert the value'''
    return datetime.strptime(str(time), timeFormat)

if __name__ == "__main__":
    app.run(debug = True)
    csrf.init_app(app)
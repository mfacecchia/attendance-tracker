from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField, BooleanField, SelectField, SubmitField, TextAreaField, DateField, ValidationError, HiddenField, TimeField
from wtforms.validators import InputRequired, Length, Regexp, DataRequired, EqualTo, Email, Optional
from datetime import date, datetime

defaultFormsClass = 'formInputBox'
defaultButtonClass = 'button'
defaultSubmitButtonClasses = 'button dark-blue'

#TODO: Add custom messages to output as flash messages
class LoginForm(FlaskForm):
    email = EmailField(name = 'Email', validators = [InputRequired(), Email()], render_kw = {'placeholder': 'Email', 'class': defaultFormsClass, 'autofocus': True})
    password = PasswordField(name = 'password', validators = [InputRequired()], render_kw = {'placeholder': 'Password', 'class': defaultFormsClass})
    remember = BooleanField(name = 'remember', label = 'Ricordami')
    submitForm = SubmitField('Login', render_kw = {'class': defaultSubmitButtonClasses})

class CourseCreationForm(FlaskForm):
    courseName = StringField(name = 'courseName', validators = [InputRequired(), Length(max = 30)], render_kw = {'placeholder': 'Nome Corso', 'class': defaultFormsClass})
    courseYear = StringField(name = 'courseYear', validators = [InputRequired(), Regexp('[1-5]'), Length(max = 1)], render_kw = {'placeholder': 'Anno Corso', 'class': defaultFormsClass})
    submitForm = SubmitField('Crea corso', render_kw = {'class': defaultSubmitButtonClasses})

class LessonCreationForm_Teacher(FlaskForm):
    subject = StringField(name = 'subject', validators = [InputRequired(), Length(max = 30)], render_kw = {'placeholder': 'Materia', 'class': defaultFormsClass})
    description = TextAreaField(name = 'description', validators = [Length(max = 1000)], render_kw = {'placeholder': 'Descrizione (opzionale)', 'class': defaultFormsClass})
    lessonDate = DateField(name = 'lessonDate', default = date.today(), validators = [InputRequired()], render_kw = {'class': defaultFormsClass})
    lessonStartTime = TimeField(name = 'lessonStartTime', validators = [InputRequired()], render_kw = {'class': defaultFormsClass}, default = datetime.strptime('09:00', '%H:%M'))
    lessonEndTime = TimeField(name = 'lessonEndTime', validators = [InputRequired()], render_kw = {'class': defaultFormsClass}, default = datetime.strptime('13:00', '%H:%M'))
    room = StringField(name = 'room', validators = [InputRequired(), Regexp('[a-zA-Z][0-9]+'), Length(min = 4, max = 4)], render_kw = {'placeholder': 'Aula (Es. A001)', 'class': defaultFormsClass})
    lessonType = SelectField(name = 'lessonType', validators = [InputRequired()], choices = [('', '-- Seleziona una tipologia --'), ('Lezione', 'Lezione'), ('Seminario', 'Seminario'), ('Laboratorio', 'Laboratorio')], render_kw = {'class': defaultFormsClass})
    #NOTE: Disabling validation in order to validate it later after the teacher is chosen from the form
    course = SelectField(name = 'course', validate_choice = False, validators = [DataRequired()], choices = [('', '-- Seleziona un corso --')], render_kw = {'class': defaultFormsClass})
    submitForm = SubmitField('Crea lezione', render_kw = {'class': defaultSubmitButtonClasses})

    def validate_lessonDate(form, lessonDate):
        '''Raises `ValidationError` if input date is behind today'''
        if lessonDate.data < date.today():
            raise ValidationError('Date cannot be lower than today')
    
    def validate_lessonEndTime(form, lessonEndTime):
        if(lessonEndTime.data < form.lessonStartTime.data):
            raise ValidationError('Lesson end time cannot be lower than lesson start time')

#Adding the assigned teacher field from the administrator (inherited class from the teacher's one)
class LessonCreationForm_Admin(LessonCreationForm_Teacher):
    assignedTeacher = SelectField(name = 'assignedTeacher', validators = [InputRequired()], choices = [('', '-- Seleziona un insegnante --')], render_kw = {'class': defaultFormsClass, 'onchange': 'getTeacherCourses()'})

class UserCreationForm(FlaskForm):
    fname = StringField(name = 'fname', validators = [InputRequired(), Length(max = 20)], render_kw = {'placeholder': 'Nome', 'class': defaultFormsClass})
    lname = StringField(name = 'lname', validators = [InputRequired(), Length(max = 20)], render_kw = {'placeholder': 'Cognome', 'class': defaultFormsClass})
    email = EmailField(name = 'email', validators = [InputRequired(), Length(max = 40), Email()], render_kw = {'placeholder': 'Email', 'class': defaultFormsClass})
    password = PasswordField(name = 'password', validators = [InputRequired(), Length(min = 10)], render_kw = {'placeholder': 'Password', 'class': defaultFormsClass})
    password_verify = PasswordField(name = 'password_verify', validators = [InputRequired(), Length(min = 10), EqualTo('password')], render_kw = {'placeholder': 'Reinserisci password', 'class': defaultFormsClass})
    role = SelectField(name = 'role', choices = [('Studente', 'Studente'), ('Insegnante', 'Insegnante'), ('Admin', 'Admin')], render_kw = {'class': defaultFormsClass, 'onchange': 'adminRoleChosen()'})
    adminVerification = BooleanField('Sei sicuro di voler creare un utente di tipo ADMIN?', validators = [DataRequired()], name = 'adminVerificationCheckbox', default = True)
    submitForm = SubmitField('Crea account', render_kw  = {'class': defaultSubmitButtonClasses})

#Inherited class from `LessonCreationForm_Admin`
class LessonUpdateForm_Teacher(LessonCreationForm_Teacher):
    lessonID = HiddenField(name = 'id')
    submitForm = SubmitField('Modifica lezione', render_kw = {'class': defaultSubmitButtonClasses})

class LessonUpdateForm_Admin(LessonCreationForm_Admin):
    lessonID = HiddenField(name = 'id')
    submitForm = SubmitField('Modifica lezione', name = 'id', render_kw = {'class': defaultSubmitButtonClasses})

class ResetPasswordForm(FlaskForm):
    email = EmailField(name = 'email', validators = [InputRequired(), Email()], render_kw = {'placeholder': 'Email', 'class': defaultFormsClass, 'autofocus': True})
    submitForm = SubmitField('Recupera la password', render_kw  = {'class': defaultSubmitButtonClasses})

class UpdateResetPasswordForm(FlaskForm):
    password = PasswordField(name = 'newPassword', validators = [InputRequired(), Length(min = 10)], render_kw = {'placeholder': 'Nuova password', 'autofocus': True, 'class': defaultFormsClass})
    password_verify = PasswordField(name = 'passwordVerify', validators = [InputRequired(), Length(min = 10), EqualTo('password')], render_kw = {'placeholder': 'Reinserisci password', 'autofocus': True, 'class': defaultFormsClass})
    submitForm = SubmitField('Aggiorna la password', render_kw  = {'class': defaultSubmitButtonClasses})

class UserUpdateForm(UserCreationForm):
    password = PasswordField(name = 'password', validators = [Optional(), Length(min = 10)], render_kw = {'placeholder': 'Password', 'class': defaultFormsClass})
    password_verify = PasswordField(name = 'password_verify', validators = [Optional(), Length(min = 10), EqualTo('password')], render_kw = {'placeholder': 'Reinserisci password', 'class': defaultFormsClass})
    submitForm = SubmitField('Modifica utente', render_kw  = {'class': defaultSubmitButtonClasses})

class UserUpdateForm_Standard(FlaskForm):
    email = EmailField(name = 'email', validators = [InputRequired(), Length(max = 40), Email()], render_kw = {'placeholder': 'Email', 'class': defaultFormsClass})
    password = PasswordField(name = 'password', validators = [Optional(), Length(min = 10)], render_kw = {'placeholder': 'Password', 'class': defaultFormsClass})
    password_verify = PasswordField(name = 'password_verify', validators = [Optional(), Length(min = 10), EqualTo('password')], render_kw = {'placeholder': 'Reinserisci password', 'class': defaultFormsClass})
    submitForm = SubmitField('Modifica utente', render_kw  = {'class': defaultSubmitButtonClasses})
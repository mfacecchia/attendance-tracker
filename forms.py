from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField, BooleanField, SelectField, SubmitField, TextAreaField, DateField, ValidationError
from wtforms.validators import InputRequired, Length, Regexp, DataRequired
from datetime import date
from app import validateCoursesSelection

defaultFormsClass = 'formInputBox'
defaultButtonClass = 'button'
defaultSubmitButtonClasses = 'button dark-blue'

class LoginForm(FlaskForm):
    email = EmailField(name = 'Email', validators = [InputRequired()], render_kw = {'placeholder': 'Email', 'class': defaultFormsClass, 'autofocus': True})
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
    room = StringField(name = 'room', validators = [InputRequired(), Regexp('[a-zA-Z][0-9]+'), Length(min = 4, max = 4)], render_kw = {'placeholder': 'Aula (Es. A001)', 'class': defaultFormsClass})
    lessonType = SelectField(name = 'lessonType', validators = [InputRequired()], choices = [('', '-- Seleziona una tipologia --'), ('Lezione', 'Lezione'), ('Seminario', 'Seminario'), ('Laboratorio', 'Laboratorio')], render_kw = {'class': defaultFormsClass})
    #NOTE: Disabling validation in order to validate it later after the teacher is chosen from the form
    course = SelectField(name = 'course', validate_choice = False, validators = [DataRequired()], choices = [('', '-- Seleziona un corso --')], render_kw = {'class': defaultFormsClass})
    submitForm = SubmitField('Crea lezione', render_kw = {'class': defaultSubmitButtonClasses})

    def validate_lessonDate(form, lessonDate):
        '''Raises `ValidationError` if input date is behind today'''
        if lessonDate.data < date.today():
            raise ValidationError('Date cannot be lower than today')

#Adding the assigned teacher field from the administrator (inherited class from the teacher's one)
class LessonCreationForm_Admin(LessonCreationForm_Teacher):
    assignedTeacher = SelectField(name = 'assignedTeacher', validators = [InputRequired()], choices = [('', '-- Seleziona un insegnante --')], render_kw = {'class': defaultFormsClass, 'onchange': 'getTeacherCourses()'})
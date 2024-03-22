from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField, BooleanField, SelectField, SubmitField, validators
from wtforms.validators import InputRequired, Length, Regexp

defaultFormsClass = 'formInputBox'
defaultButtonClass = 'button'

class LoginForm(FlaskForm):
    email = EmailField(name = 'Email', validators = [InputRequired()], render_kw = {'placeholder': 'Email', 'class': defaultFormsClass, 'autofocus': True})
    password = PasswordField(name = 'password', validators = [InputRequired()], render_kw = {'placeholder': 'Password', 'class': defaultFormsClass})
    remember = BooleanField(name = 'remember', label = 'Ricordami')
    submitForm = SubmitField('Login', render_kw = {'class': f"{defaultButtonClass} dark-blue"})

class CourseCreationForm(FlaskForm):
    courseName = StringField(name = 'courseName', validators = [InputRequired(), Length(max = 30)], render_kw = {'placeholder': 'Nome Corso', 'class': defaultFormsClass})
    courseYear = StringField(name = 'courseYear', validators = [InputRequired(), Regexp('[1-5]'), Length(max = 1)], render_kw = {'placeholder': 'Anno Corso', 'class': defaultFormsClass})
    submitForm = SubmitField('Crea corso', render_kw = {'class': f"{defaultButtonClass} dark-blue"})
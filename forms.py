from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField, BooleanField, SelectField, SubmitField, validators
from wtforms.validators import InputRequired, Length

defaultFormsClass = 'formInputBox'
defaultButtonClass = 'button'

class LoginForm(FlaskForm):
    email = EmailField(name = 'Email', validators = [InputRequired()], render_kw = {'placeholder': 'Email', 'class': defaultFormsClass, 'autofocus': True})
    password = PasswordField(name = 'password', validators = [InputRequired()], render_kw = {'placeholder': 'Password', 'class': defaultFormsClass})
    remember = BooleanField(name = 'remember', label = 'Ricordami')
    submitForm = SubmitField('Login', render_kw = {'class': f"{defaultButtonClass} dark-blue"})
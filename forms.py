from wtforms import Form, StringField, EmailField, PasswordField, BooleanField, SelectField, SubmitField, validators
from wtforms.validators import InputRequired, Length

defaultFormsClass = 'formInputBox'
defaultButtonClass = 'button'

class LoginForm(Form):
    Email = EmailField(validators = [InputRequired()], render_kw = {'placeholder': 'Email', 'class': defaultFormsClass})
    password = PasswordField(validators = [InputRequired()], render_kw = {'placeholder': 'Password', 'class': defaultFormsClass})
    remember = BooleanField('Ricordami')
    submitForm = SubmitField('Login', render_kw = {'class': defaultButtonClass})
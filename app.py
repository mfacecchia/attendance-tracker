from flask import Flask, render_template, url_for, request

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register')
def register():
    return render_template('register.html')

#FIXME: Change handle URL with UID
@app.route("/register/handle", methods = ['POST'])
def handle_form_data():
    firstName = request.form.get('fname')
    lastName = request.form.get('lname')
    email = request.form.get('email')
    pw = request.form.get('password')
    role = request.form.get('role')

    return f"<p>{firstName}</p>, <p>{lastName}</p>, <p>{email}</p>, <p>{pw}</p>, <p>{role}</p>"


if __name__ == "__main__":
    app.run(debug = True)
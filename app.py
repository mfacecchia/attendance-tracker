from flask import Flask, render_template, url_for, request, redirect

roleOptions = ['Student', 'Teacher']

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register')
def register():
    return(render_template('register.html', roleOptions = roleOptions))

@app.route('/request')
def handle_request(methods = 'POST'):
    pass


if __name__ == "__main__":
    app.run(debug = True)
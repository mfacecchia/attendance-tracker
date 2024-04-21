<img src = "https://github.com/mfacecchia/attendance-tracker/assets/86726458/0422693b-bbf6-4111-81d3-4ab67696a74a">
<h1 align = 'center'>Attendance Tracker</h1>
<p align = 'center'>Simple but useful app to easily record, manage, and track teachers' and students' attendances in schools.</p>

<h2>Table of Contents</h2>
<a href = "#built-in">Built in - Technologies</a><br>
<a href = "#modules-references">Modules References</a><br>
<a href = "#importing-modules">Importing modules</a><br>
<a href = "#environmental-variables">Environmental Variables</a><br>
<a href = "#db-er">Database Entity Relationship model</a><br>
<a href = "#app-routes">App Routes</a><br>
<a href = "#hashing-methods">Hashing methods</a><br>
<a href = "#functions">Functions</a>

<h2 id = "built-in">Built in - Technologies</h2>
<img src = "https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white">
<img src = "https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white">
<img src = "https://img.shields.io/badge/HTML-239120?style=for-the-badge&logo=html5&logoColor=white">
<img src = "https://img.shields.io/badge/CSS-239120?&style=for-the-badge&logo=css3&logoColor=white">
<img src = "https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white">
<img src = "https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black">
<img src = "https://img.shields.io/badge/chart.js-F5788D.svg?style=for-the-badge&logo=chart.js&logoColor=white">
<img src = "https://img.shields.io/badge/MySQL-00000F?style=for-the-badge&logo=mysql&logoColor=white">

<h2 id = "modules-references">Modules References</h2>
<h4>Core Functionalities</h4>
<a href = "https://flask.palletsprojects.com/en/3.0.x/">Flask app</a> |
<a href = "https://pythonhosted.org/Flask-Mail/">Flask Mail</a> |
<a href = "https://flask-wtf.readthedocs.io/en/1.2.x/">Flask WTForms</a> |
<a href = "https://dev.mysql.com/doc/connector-python/en/">MySQL Connector</a> |
<a href = "https://docs.python.org/3/library/os.html">OS</a> |
<a href = "https://docs.python.org/3/library/datetime.html">Datetime</a> |
<a href = "https://tailwindcss.com/docs/installation">Tailwind CSS</a> |
<a href = "https://www.chartjs.org">ChartJS</a> |
<a href = "https://api.jquery.com">JQuery</a>
<h4>Hashing & security</h4>
<a href = "https://argon2-cffi.readthedocs.io/en/stable/">Argon2</a> |
<a href = "https://docs.python.org/3/library/base64.html">Base64</a> |
<a href = "https://flask-wtf.readthedocs.io/en/0.15.x/csrf/">Anti CSRF Token</a>
<h4>Login Methods</h4>
<a href = "https://docs.authlib.org/en/latest/">Authlib's OAuth</a> |
<a href = "https://googleapis.github.io/google-api-python-client/docs/oauth.html#flow">Google's OAuth Flow</a>

<h2 id = "importing-modules">Importing modules</h2>
<p>To quickly import all modules used in this project, a requirements file has been provided so simply execute the following command</p>

```
pip3 install -r requirements.txt
```
<p>and you'll be good to go.</p>
<b>DISCLAIMER: It is recommended to install all the modules after <a href = "https://docs.python.org/3/library/venv.html">creating a virtual environment</a> to avoid possible module conflicts with other projects in your drive.</b>

<h2 id = "environmental-variables">Environmental Variables</h2>
<p>All the application's related variables such as the secret key, the <a href = "https://pythonhosted.org/Flask-Mail/">Flask Mail's configuration data</a>, <a href = "https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/authorizing-oauth-apps#web-application-flow">GitHub's OAuth URLs & app's secrets</a> and <a href = "https://googleapis.github.io/google-api-python-client/">Google's</a> are securely stored in the virtual environment (not included in this repository for security purposes since personal data is used).</p>
<p>Below a list and explanation of all the used virtual environment's variables.</p>
<table>
  <tr>
    <th>Variable Name</th>
    <th>Usage</th>
  </tr>
  <tr>
    <td>FLASK_SECRET</td>
    <td>Flask's secret key to securely manage all sessions and cookies data (as stated on <a href = "https://flask.palletsprojects.com/en/3.0.x/quickstart/#sessions">Flask's API Documentation</a>)</td>
  </tr>
  <tr>
    <td>MAIL_SERVER</td>
    <td>Flask mail SMTP address (as stated on <a href = "https://pythonhosted.org/Flask-Mail/#configuring-flask-mail">Flask Mail documentation</a>)</td>
  </tr>
  <tr>
    <td>MAIL_PORT</td>
    <td>Flask mail port (as stated on <a href = "https://pythonhosted.org/Flask-Mail/#configuring-flask-mail">Flask Mail documentation</a>)</td>
  </tr>
  <tr>
    <td>MAIL_USERNAME</td>
    <td>Flask mail address (as stated on <a href = "https://pythonhosted.org/Flask-Mail/#configuring-flask-mail">Flask Mail documentation</a>)</td>
  </tr>
  <tr>
    <td>MAIL_PASSWORD</td>
    <td>Flask mail password (as stated on <a href = "https://pythonhosted.org/Flask-Mail/#configuring-flask-mail">Flask Mail documentation</a>) (used in this project port 587)</td>
  </tr>
  <tr>
    <td>GITHUB_CLIENT_ID</td>
    <td>Github OAuth app client ID (as stated on <a href = "https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/authenticating-to-the-rest-api-with-an-oauth-app#registering-your-app">Github RESI API Documentation</a>)</td>
  </tr>
  <tr>
    <td>GITHUB_CLIENT_SECRET</td>
    <td>Github OAuth app client secret (as stated on <a href = "https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/authenticating-to-the-rest-api-with-an-oauth-app#registering-your-app">Github RESI API Documentation</a>)</td>
  </tr>
  <tr>
    <td>DB_USERNAME</td>
    <td>Database user username (as stated on <a href = "https://dev.mysql.com/doc/connector-python/en/connector-python-connectargs.html">MySQL Connector Documentation</a>)</td>
  </tr>
  <tr>
    <td>DB_PWORD</td>
    <td>Database user password (as stated on <a href = "https://dev.mysql.com/doc/connector-python/en/connector-python-connectargs.html">MySQL Connector Documentation</a>)</td>
  </tr>
  <tr>
    <td>DB_HOSTNAME</td>
    <td>Database host address (as stated on <a href = "https://dev.mysql.com/doc/connector-python/en/connector-python-connectargs.html">MySQL Connector Documentation</a>)</td>
  <tr>
    <td>DB_NAME</td>
    <td>Database name (as stated on <a href = "https://dev.mysql.com/doc/connector-python/en/connector-python-connectargs.html">MySQL Connector Documentation</a>)</td>
  </tr>
</table>
<b>NOTE:</b> For this project the database is locally hosted so the environmental values of DB_USERNAME, DB_PWORD, DB_HOSTNAME, DB_NAME will be `root`, `""`, `localhost` (port 3306), `Attendance_Tracker`

<h2 id = "db-er">Database Entity Relationship model</h2>
<img alt="Database Entity Relationship image" src="https://github.com/mfacecchia/attendance-tracker/assets/86726458/996a813f-a497-4f65-855a-59aa687edd81">
<p>If you want to test this project on your own device you can import the <a href = "https://github.com/mfacecchia/attendance-tracker/blob/main/Attendance_Tracker_dump.sql">database tables dump</a> as well.</p>

<h2 id = "app-routes">App Routes</h2>
<table>
  <tr>
    <th>Route</th>
    <th>Description</th>
  </tr>
  <tr>
    <td>/</td>
    <td>Landing page. Accessible to anyone who doesn't have an account or is not logged in. If logged in, the user will be automatically redirected to the screening page.</td>
  </tr>
  <tr>
    <td>/login</td>
    <td>Login form. Outputs the form with Email and password input and validates the input passed through a POST request. If already logged in, the user will be automatically redirected to the screening page. For more information about hashed password verification, <a href = "#hashing-methods">this section</a> will better explain the process.</td>
  </tr>
  <tr id = "forgot-password">
    <td>/forgot-password</td>
    <td>Outputs the form with Email input and sends an email to that address with a reset password link. Accessible via the `/login` page. For more information about Email sending function and reset password link GET parameters, <a href = "#password-reset">this section</a> will better explain the process.</td>
  </tr>
  <tr id = "update-password">
    <td>/user/updatepassword</td>
    <td>Ouptuts the form with Password and Verify Password. Accessible via Email reset password link and after the first login on the application. Input is then validated and the user's password gets updated on the database. For more information about password verification and hashing, <a href = "#hashing-methods">this section</a> will better explain the process.</td>
  </tr>
  <tr>
    <td>/auth/github</td>
    <td>Redirects to GitHub's OAuth App authorization. For more information about GitHub's OAuth App Authorization process, please visit <a href = "https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/authenticating-to-the-rest-api-with-an-oauth-app">the official documentation</a>.</td>
  </tr>
  <tr>
    <td>/auth/github/callback</th>
    <td>GitHub OAuth App callback page, used to manage GitHub OAuth REST API return values. For more information about GitHub's OAuth App Authorization process, please visit <a href = "https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/authenticating-to-the-rest-api-with-an-oauth-app">the official documentation</a>.</td>
  </tr>
  <tr id = "github-oauth-callback">
    <td>/auth/github/disconnect</td>
    <td>Removes GitHub Account user ID from the database</td>
  <tr>
    <td>/auth/google</td>
    <td>Redirects to Google's OAuth App Authorization. For more information about Google's OAuth App Authorization process, please visit <a href = "https://developers.google.com/identity/protocols/oauth2">the official documentation</a>.</td>
  </tr>
  <tr>
    <td>/auth/google/callback</td>
    <td>Google OAuth App callback page, used to manage Google OAuth API return values. For more information about Google's OAuth App Authorization process, please visit <a href = "https://developers.google.com/identity/protocols/oauth2">the official documentation</a>.</td>
  </tr>
  <tr id = "google-oauth-callback">
    <td>/auth/google/disconnect</td>
    <td>Removes Google Account user ID from the database</td>
  </tr>
  <tr>
    <td>/user</td>
    <td>User screening. Outputs all the user's related information such as name, role, and last login time as well as a list of all upcoming lessons, a user creation form (ADMIN user role only), a lesson creation form (ADMIN and TEACHER user roles only), a course creation form (ADMIN user role only), a pie chart of attended/not attended lessons percentage (STUDENT and TEACHER user roles only) or a bar chart of the total number of attendances subdivided per lesson date and course name in a chosen range of 7 days, 14 days or 30 days (TEACHER and ADMIN user roles only). For more information about Chart generation, <a href = "#chart-generation">this section</a> will better explain the process. Accessible only if a <a href = "https://flask.palletsprojects.com/en/3.0.x/api/#sessions">valid session</a> is open, otherwise redirects to the login page with an error message.</td>
  </tr>
  <tr id = "create-user">
    <td>/user/create</td>
    <td>User creation form and data insertion in the database (ADMIN user role only). For more information about form validation, the <a href = "https://wtforms.readthedocs.io/en/2.3.x/validators/?highlight=validators#module-wtforms.validators">official flask-wtf documentation</a> will better explain how the whole validation process works.</td>
  </tr>
  <tr id = "create-lesson">
    <td>/lesson/create</td>
    <td>Lesson creation form and data insertion in the database (ADMIN and TEACHER user roles only). For more information about form validation, the <a href = "https://wtforms.readthedocs.io/en/2.3.x/validators/?highlight=validators#module-wtforms.validators">official flask-wtf documentation</a> will better explain how the whole validation process works.</td>
  </tr>
  <tr id = "lessons-list">
    <td>/lesson/list</td>
    <td>Shows a list of all the upcoming lessons with a button to manage the lesson's attendances (if the lesson's date is the same as the current date) (ADMIN and TEACHER user roles only), a button to update all lesson's parameters such as subject, description, time and date, and more (ADMIN and TEACHER user roles only), and a button to delete the lesson. The page shows 10 lessons per page, ordered per lesson date. The list varies based on the user role accessing the page; if the role is STUDENT or TEACHER, the list will show only the upcoming lessons for their specific enrolled courses.</td>
  </tr>
  <tr id = "update-lesson">
    <td>/lesson</td>
    <td>Lesson screening. Outputs a form with all lesson's information and a button to submit the modifications and update the database (ADMIN and TEACHER user roles only).</td>
  </tr>
  <tr>
    <td>/lesson/register-attendance</td>
    <td>Lesson screening. Outputs the selected lesson name as well as a list of all enrolled students and a checkbox to record students' attendances (ADMIN and TEACHER user roles only).</td>
  </tr>
  <tr>
    <td>/lesson/attendances</td>
    <td>Custom API that returns a JSON file about all lessons attendances count in a defined range. For more information about this API, <a href = "#lessons-attendances-count-api">this section</a> will better explain the process.</td>
  </tr>
  <tr>
    <td>/lessons/attendances/percentage</td>
    <td>Custom API that returns a JSON file about all lessons attendances/non-attendances percentage rate in a defined range. For more information about this API, <a href = "#lessons-attendances-rate-api">this section</a> will better explain the process.</td>
  </tr>
  <tr id = "create-course">
    <td>/course/create</td>
    <td>Course creation form and data insertion in the database (ADMIN user role only). For more information about form validation, the <a href = "https://wtforms.readthedocs.io/en/2.3.x/validators/?highlight=validators#module-wtforms.validators">official flask-wtf documentation</a> will better explain how the whole validation process works.</td>
  </tr>
  <tr id = "users-list">
    <td>/user/list</td>
    <td>Shows a list of all users registered in the platform with a button to update each user's parameters such as name, surname, enrolled courses, and more (ADMIN user role only), and a button to delete the user from the Database (ADMIN user role only). The page shows 10 students per page, ordered per role (Admin, then Teachers, and then Students).</td>
  </tr>
  <tr id = "update-user">
    <td>/user/select</td>
    <td>Outputs a form to update chosen user's parameters such as name, surname, enrolled courses, and more (ADMIN user role only). The inputted data is then processed based on the session user role who is making the request; if the user role is ADMIN, then the selected user data will be related to all selected user's information, otherwise, the parameters to update will be just Email and Password if the session user role is STUDENT or TEACHER (in this case, the update request will be processed based on self user's data because only the ADMIN can update other user's parameters). For more information about form validation, the <a href = "https://wtforms.readthedocs.io/en/2.3.x/validators/?highlight=validators#module-wtforms.validators">official flask-wtf documentation</a> will better explain how the whole validation process works.</td>
  </tr>
  <tr>
    <td>/user/logout</td>
    <td>Clears the user <a href = "https://flask.palletsprojects.com/en/3.0.x/api/#sessions">session</a> and logs the user out of the application.</td>
  </tr>
  <tr>
    <td>/cookie-policy</td>
    <td>Cookie Policy page randomly generated from <a href = "https://termly.io">Termly policies generator tool</a>.</td>
  </tr>
  <tr>
    <td>/terms-and-conditions</td>
    <td>Terms and conditions page randomly generated from <a href = "https://termly.io">Termly policies generator tool</a>.</td>
  </tr>
  <tr>
    <td>/privacy</td>
    <td>Privacy policy page randomly generated from <a href = "https://termly.io">Termly policies generator tool</a>.</td>
  </tr>
</table>

<h2 id = "hashing-methods">Hashing methods</h2>
<p>All user-related sensitive data such as passwords are securely hashed and stored in the database using <a href = "https://en.wikipedia.org/wiki/Argon2">Argon2id algorithm</a>. To manage and verify such data, <a href = "https://argon2-cffi.readthedocs.io/en/stable/">Argon2-cffi</a> Python module is being used, in particular the `PasswordHasher` class and its relative methods <a href = "https://argon2-cffi.readthedocs.io/en/stable/api.html#argon2.PasswordHasher.verify">verify</a> for login and reset password verification functionalities and <a href = "https://argon2-cffi.readthedocs.io/en/stable/api.html#argon2.PasswordHasher.hash">hash</a> for user creation and reset password functionalities. Non-matching passwords after the <a href = "https://argon2-cffi.readthedocs.io/en/stable/api.html#argon2.PasswordHasher.verify">verify</a> function is called are managed with Argon2 module built-in <a href = "https://argon2-cffi.readthedocs.io/en/stable/api.html#argon2.exceptions.VerifyMismatchError">VerifyMismatchError exception</a>.</p>
<p>Instead, the <a href = "#update-password">password reset route</a> uses an authenticity request method that requires the GET parameters `mail` and `uid` to be hashed with base64 algorithm in order to lower the possibility for an attacker to guess a user email and user ID combination and so reset his password.</p>

<h2 id = "functions">Functions</h2>
<h3>connectToDB()</h3>
<p>Starts a connection to the database with the given data through <a href = "https://dev.mysql.com/doc/connector-python/en/connector-python-api-mysqlconnection-connect.html">MySQLConnector.connect() function</a>. Connection not established error is managed with <a href = "https://dev.mysql.com/doc/connector-python/en/connector-python-api-errors-error.html">MySQLConnector.Error</a> error.</p>
<p>Returns <a href = "https://dev.mysql.com/doc/connector-python/en/connector-python-example-connecting.html">MySQLConnection object</a> or `False` if the connection to Database fails for some reason.</p>

<h3>getCourses()</h3>
<p>Executes a simple `select` query on the database and updates the global list `courses` with all the formatted courses's names and years.</p>
<p>Returns the formatted output of <a href = "https://dev.mysql.com/doc/connector-python/en/connector-python-api-mysqlcursor-execute.html">cursor.execute()</a>.
<p>An example of output from this function will be:</p>

```
[
  '1a Sviluppo software',
  '2a Cybersecurity',
  '1a Sviluppo web'
]
```
<p>For more information about query to list conversion, <a href = "#get-values-from-query">this section</a> will better explain the process.</p>

<h3>update_user_data()</h3>
<p>Manages the function to call based on the session's user's role and the given uid passed as a parameter. The function takes as parameters the form to be processed in the to-be-called function and the uid as optional which will represent the selected user ID if the ADMIN is requesting to update some chosen user. This function calls the <a href = "update-data-as-user">updateDataAsUser function</a> if the session's user role is STUDENT or TEACHER or the `uid` parameter is not given (means that the ADMIN wants to update his information), otherwise the <a href = "#update-data-as-admin">updateDataAdAdmin function</a> with the passed `uid` and `form` as function parameters. Returns `True` if the callback function returns `True` as well, otherwise `False`.</p>

<h3 id = "get-values-from-query">getValuesFromQuery()</h3>
<p>Gets a <a href = "https://dev.mysql.com/doc/connector-python/en/connector-python-api-mysqlconnection-cursor.html">MySQLConnector cursor</a> as a parameter and returns a list with dictionaries as list's items with cursor columns names as keys and obtained values as dictionary values. Briefly, this function will iterate through the entire cursor and create a dictionary for each query returned column. If the cursor is empty this function will return an empty list.</p>
<p>This function will return a list like the following</p>

```
[
  {
    'nomeCorso': 'Sviluppo Software',
    'annoCorso': '2023-2024'
  },
  {
    'nomeCorso': 'Sviluppo Web',
    'annoCorso': '2023-2024'
  }
]
```

<h3>updateLastLoginTime()</h3>
<p>Programmatically updates the user's last login time on the database by executing an `update` SQL query on the database. The user is defined by the session's userID value and the current time is obtained from <a href = "https://docs.python.org/3/library/datetime.html#datetime.date.today">date.today()</a> function.</p>
<p>Returns the formatted current date in `%d/%m/%Y` format by using <a href = "https://docs.python.org/3/library/datetime.html#datetime.date.strftime">date.strftime()</a> function.</p>

<h3>checkUserGithubConnection()</h3>
<p>Checks if the user has a linked Github account. The user is defined by the session's userID value</p>
<p>Returns a boolean value corresponding `True` if the defined user has a linked Github Account or `False` if the Database's "githubID" field is empty</p>

<h3>linkGithubAccount()</h3>
<p>Updates user's "githubID" database column with the GitHub account id passed as function parameter from <a href = "#github-oauth-callback">GitHub OAuth API return values</a>. Before updating the column, a verification is done; a <a href = "https://dev.mysql.com/doc/connector-python/en/connector-python-api-mysqlconnection-cursor.html">cursor</a> gets instantiated and checks if the obtained GitHub user id is already linked to an account with a simple `select` query. If the cursor's result contains no rows (which means that no users have linked that specific GitHub account to their attendance tracker account), then it is possible to update the user's `githubID` column and the session's related `githubConnected` value is set to `True`.</p>
<p>Returns `True` if the column is updated, otherwise `False` in all other cases.</p>

<h3>loginWithGithub()</h3>
<p>Looks for GitHub user ID obtained from the GitHub account ID from <a href = "#github-oauth-callback">GitHub OAuth API return values</a> and executes a `select` query to obtain the relative user ID from the database. If the user is found, a session with all needed user information gets created.</p>
<p>Returns `True` if the GitHub user ID was found in the database, otherwise `False`.</p>

<h3>checkUserGoogleConnection()</h3>
<p>Checks if the user has a linked Google account. The user is defined by the session's userID value</p>
<p>Returns a boolean value corresponding `True` if the defined user has a linked Google Account or `False` if the Database's "googleID" field is empty</p>

<h3>linkGoogleAccount()</h3>
<p>Updates user's "googleID" database column with the Google account ID passed as function parameter from <a href = "#google-oauth-callback">Google OAuth API return values</a>. Before updating the column, a verification is done; a <a href = "https://dev.mysql.com/doc/connector-python/en/connector-python-api-mysqlconnection-cursor.html">cursor</a> gets instantiated and checks if the obtained Google user id is already linked to an account with a simple `select` query. If the cursor's result contains no rows (which means that no users have linked that specific Google account to their attendance tracker account), then it is possible to update the user's `googleID` column and the session's related `googleConnected` value is set to `True`.</p>
<p>Returns `True` if the column is updated, otherwise `False` in all other cases.</p>

<h3>loginWithGoogle()</h3>
<p>Looks for Google user ID obtained from the Google account ID from <a href = "#google-oauth-callback">Google's OAuth API return values</a> and executes a `select` query to obtain the relative user ID from the database. If the user is found, a session with all needed user information gets created.</p>
<p>Returns `True` if the Google user ID was found in the database, otherwise `False`.</p>

<h3>validateFormInput()</h3>
<p>Validates form user input by checking if the input data is not an empty string.</p>
<p>Returns `True` if the passed string is empty, otherwise `False`</p>

<h3>getUsersList()</h3>
<p>Obtains all users from the database by executing a `select` query.</p>
<p>Returns the formatted output of <a href = "https://dev.mysql.com/doc/connector-python/en/connector-python-api-mysqlcursor-execute.html">cursor.execute()</a>.</p>
<p>The returning list of this function will look something like this:</p>

```
[
  {
    'userID': 1,
    'Nome': 'Mario',
    'Cognome': 'Rossi',
    'Tipologia': 'Studente',
    'nomeCorso': 'Sviluppo software',
    'annoCorso': 1
  },
  {
    'userID': 2,
    'Nome': 'Luigi',
    'Cognome': 'Verdi',
    'Tipologia': 'Insegnante',
    'nomeCorso': 'Cybersecurity',
    'annoCorso': 2
  }
]
```
<p>For more information about query to list conversion, <a href = "#get-values-from-query">this section</a> will better explain the process.</p>

<h3>getUserData()</h3>
<p>Gets all user's related data by executing a `select` query. The user is defined by the passed function's parameter `uid`.</p>
<p>Returns the formatted output of <a href = "https://dev.mysql.com/doc/connector-python/en/connector-python-api-mysqlcursor-execute.html">cursor.execute()</a> in form of dictionary.</p>
<p>An example output of this function is:</p>

```
{
  'userID': 1,
  'Nome': 'Mario'
  'Cognome': 'Rossi',
  'Tipologia': 'Studente',
  'Email': 'mariorossi@mr.com',
  'nomeCorso': 'Sviluppo software',
  'annoCorso': 1
}
```
<p>For more information about query to dictionary conversion, <a href = "#get-values-from-query">this section</a> will better explain the process.</p>

<h3 id = "update-data-as-admin">updateDataAsAdmin()</h3>
<p>Updates all selected user's data (ADMIN user only). Takes as parameters the selected user ID and the form that will be used to get the data from and to be used to update the database. For more information about password hashing, <a href = "#hashing-methods">this section</a> will better explain the process.</p>

<h3 id = "update-data-as-admin">updateDataAsUser()</h3>
<p>Updates all selected user's data. Takes as parameters the form that will be used to get the data from and to be used to update the database. For more information about password hashing, <a href = "#hashing-methods">this section</a> will better explain the process.</p>

<h3>validateCoursesSelection()</h3>
<p>Gets all courses' names and the relative years as parameters (MUST be type list()) and executes a query for each item to check if the actual selection exists. Used in user <a href = "#create-user">creation</a> and <a href = "#update-user">update</a> and lesson <a href = "#create-lesson">creation</a> and <a href = "#update-lesson">update</a>. Also allows a filter for the validation based on the chosen userID to be checked (preference passed in the `userFilter` function parameter). Returns `False` if the DB response returns `None`, else `True` if all requests return a value</p>

<h3>getCustomMessage()</h3>
<p>Returns a custom message based on the system clock time and a matrix with the default messages and the time ranges which will be selected to be printed out on the user screening page.</p>

<h3>getUserCourses()</h3>
<p>Getting all courses from the query and creating a single formatted list with all the obtained ones</p>
<p>An example of list output will be:</p>

```
[
  '1a Sviluppo software',
  '2a Cybersecurity'
]
```

<h3>deleteUser()</h3>
<p>Removes a defined user from the database based on the passed parameter `uid`.</p>

<h3>getLessonsList()</h3>
<p>Executes a query and returns all the upcoming lessons based on user type and enrolled courses filters, and the total number of lessons.
Takes as parameters a `limit` variable used to limit the number of results and a `page` variable used to get the next `limit`ed results.
Also allows to get the upcoming lessons of a determined user by passing the `uid` and `isTeacher` parameters which respectively represent the userID to get the lessons of and, if the user is a Teacher, the `isTeacher` value must be set to `True`</p>
<p>Returns a list with a dictionary for each list index and the total number of obtained lessons</p>

```
[
  [
    {
      'idLezione': 1,
      'Materia': 'Python',
      'Descrizione': 'Sviluppo app in Flask',
      'dataLezione': '2024-03-27',
      'oraInizio': '09:00',
      'oraFine': '13:00',
      'aula': 'A001',
      'Tipologia': 'Laboratorio',
      'nomeCorso': '1a Sviluppo software',
      'Presenza': 1
    },
    {
      'idLezione': 2,
      'Materia': 'Sviluppo siti web',
      'Descrizione': 'TailwindCSS e JS',
      'dataLezione': '2024-03-28',
      'oraInizio': '09:30',
      'oraFine': '13:30',
      'aula': 'A003',
      'Tipologia': 'Lezione',
      'nomeCorso': '1a Sviluppo web',
      'Presenza': 0
    }
  ], 2
]
```
With a filter on the lesson's course if the request is being made from a STUDENT or TEACHER user role.

<h3>verifyUserExistence()</h3>
<p>Verifies if the user exists before sending the recover password email. Used in <a href = "#forgot-password">user password recovery function</a>.
Returns its relative `userID` if the query returns a value, otherwise `False`</p>

<h3>b64_encode_decode()</h3>
<p>Takes a string as input parameter and returns its relative base64 encoded/decoded value. If `encode` parameter is `True`, the string will be encoded, if it's `False` it will be decoded. For more information about encoding and decoding with base64, <a href = "#hashing-methods">this section</a> will better explain the process.</p>

<h3>selectUsersFromCourse()</h3>
<p>Executes a query and returns a list of all the users attending a defined course. Course is chosen based on the function parameters `courseName` and `courseYear`.</p>
<p>An example output of this function will be:</p>

```
[
  {
    'userID': 1,
    'Tipologia': 'Insegnante'
  },
  {
    'userID': 2,
    'Tipologia': 'Studente'
  },
  {
    'userID': 3,
    'Tipologia': 'Studente'
  },
  {
    'userID': 4,
    'Tipologia': 'Studente'
  }
]
```

<h3 id = "get-lessons-attendances-count">getLessonsAttendancesCount()</h3>
<p>Executes a query and returns in the form of JSON the count of attendances subdivided per lesson date and course ID. Takes as parameters a `range` which will be used to get all the lessons starting from the current date (obtained from <a href = "https://docs.python.org/3/library/datetime.html#datetime.date.today">datetime's date.today</a> class' function) to `range` days before.</p>
<p>The output of this API will be:</p>

```
[
  {
    "conteggioPresenze": 5,
    "dataLezione": "20/03/2024",
    "nomeCorso": "1a Cybersecurity"
  },
  {
    "conteggioPresenze": 14,
    "dataLezione": "20/03/2024",
    "nomeCorso": "1a Cybersecurity"
  },
  {
    "conteggioPresenze": 11,
    "dataLezione": "20/03/2024",
    "nomeCorso": "1a Cybersecurity"
  },
  {
    "conteggioPresenze": 8,
    "dataLezione": "20/03/2024",
    "nomeCorso": "1a Sviluppo software"
  },
  {
    "conteggioPresenze": 9,
    "dataLezione": "20/03/2024",
    "nomeCorso": "2a Sviluppo software"
  },
  {
    "conteggioPresenze": 1,
    "dataLezione": "20/03/2024",
    "nomeCorso": "3a Sviluppo software"
  },
  {
    "conteggioPresenze": 6,
    "dataLezione": "20/03/2024",
    "nomeCorso": "1a Sviluppo web"
  },
  {
    "conteggioPresenze": 3,
    "dataLezione": "20/03/2024",
    "nomeCorso": "2a Sviluppo web"
  },
  {
    "conteggioPresenze": 7,
    "dataLezione": "21/03/2024",
    "nomeCorso": "1a Sviluppo web"
  },
  {
    "conteggioPresenze": 2,
    "dataLezione": "24/03/2024",
    "nomeCorso": "1a Cybersecurity"
  }
]
```

<h3>reformatResponse()</h3>
<p>Gets a list and converts each obtained course from the <a href = "#get-lessons-attendances-count">`getLessonsAttendancesCount` function</a> to the desired format. Returns a list of dictionaries like this one:</p>

```
[
  {
    "nomeCorso": "1a Cybersecurity"
    "dataLezione": "20/03/2024",
    "conteggioPresenze": 5,
  },
  {
    "nomeCorso": "1a Cybersecurity"
    "dataLezione": "20/03/2024",
    "conteggioPresenze": 14,
  },
  {
    "nomeCorso": "1a Cybersecurity"
    "dataLezione": "20/03/2024",
    "conteggioPresenze": 11,
  },
  {
    "nomeCorso": "1a Sviluppo software"
    "dataLezione": "20/03/2024",
    "conteggioPresenze": 8,
  },
  {
    "conteggioPresenze": 9,
    "dataLezione": "20/03/2024",
    "nomeCorso": "2a Sviluppo software"
  },
  {
    "nomeCorso": "3a Sviluppo software"
    "dataLezione": "20/03/2024",
    "conteggioPresenze": 1,
  },
  {
    "nomeCorso": "1a Sviluppo web"
    "dataLezione": "20/03/2024",
    "conteggioPresenze": 6,
  },
  {
    "nomeCorso": "2a Sviluppo web"
    "dataLezione": "20/03/2024",
    "conteggioPresenze": 3,
  },
  {
    "nomeCorso": "1a Sviluppo web"
    "dataLezione": "21/03/2024",
    "conteggioPresenze": 7,
  },
  {
    "nomeCorso": "1a Cybersecurity"
    "dataLezione": "24/03/2024",
    "conteggioPresenze": 2,
  }
]
```

<h3>getUserEnrolledCourses()</h3>
<p>Executes a query and gets all courses' names and years based on function parameter `uid`. If the `uid` parameter is not passed, the default value will be the user's session value `uid`. Returns a list if the query returns valid values, else `False` if the connection to the database fails.</p>
<p>An example of a possible returning list can be:</p>

```
[
  {
    'userID': 1,
    'Tipologia': 'Insegnante'
  },
  {
    'userID': 2,
    'Tipologia': 'Studente'
  },
  {
    'userID': 3,
    'Tipologia': 'Studente'
  },
  {
    'userID': 4,
    'Tipologia': 'Studente'
  }
]
```

<h3>getTeachersList()</h3>
<p>Executes a query and returns a list of all teachers' IDs, names, and surnames if the query returns valid values, otherwise `False` if the connection to the Database fails.</p>
<p>This function will return a list similar to the following</p>

```
[
  {
    'id': 10,
    'Nome': 'Francesco Verdi',
  },
  {
    'id': 11,
    'Nome': 'Mario Grigi',
  },
  {
    'id': 12,
    'Nome': 'Paolo Bianchi',
  }
]
```

<h3>isPageNumberValid()</h3>
<p>Gets the `page` parameter from the URL and validates it based on some basic controls. Used in <a href = "#lessons-list">/lesson/list</a> and <a href = "#users-list">/user/list</a> routes. Returns the `page` value if it's valid, otherwise `False` if not.</p>

<h3>getLessonInfo()</h3>
<p>Executes a query and obtains all the information related to the lesson's `lessonID` function parameter. Returns a dictionary with all useful lesson information such as Subject, description, date and time, and all assigned teacher-related information.</p>
<p>The returned dictionary will be:</p>

```
{
  idLezione: 1,
  'Materia': 'Python',
  'Descrizione': 'Sviluppo app in Flask',
  'dataLezione': '2024-03-27',
  'oraInizio': '09:00',
  'oraFine': '12:00',
  'aula': 'A001',
  'Tipologia': 'Laboratorio',
  'idInsegnante': 1,
  'Nome': 'Mario Rossi',
  'nomeCorso': '1a Sviluppo software'
}
```

<h3>update_lesson_data()</h3>
<p>Updates lesson's data based on form submitted and validated values. Used in <a href = "#update-lesson">/lesson route</a>. Returns `True` if the process succeeds, otherwise `False` with a flashed message if the process catches an error.</p>

<h3>timedeltaConverter()</h3>
<p>Converts a given `timedelta` type to datetime. Takes as parameters the actual `timedelta` `time` and its relative format to correctly convert the value. Returns the converted time.</p>

<img src = "https://github.com/mfacecchia/attendance-tracker/assets/86726458/0422693b-bbf6-4111-81d3-4ab67696a74a">
<h1 align = 'center'>Attendance Tracker</h1>
<p align = 'center'>Simple but useful app to easily record, manage and track teachers and students' attendances in schools.</p>

<h2>Table of Contents</h2>
<a href = "#built-in">Built in</a><br>
<a href = "#environmental-variables">Environmental Variables</a><br>
<a href = "#db-er">Database Entity Relationship model</a><br>
<a href = "#app-routes">App Routes</a><br>
<a href = "#hashing-methods">Hashing methods</a><br>
<a href = "#functions">Functions</a>

<h2 id = "built-in">Built in</h2>
<img src = "https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white">
<img src = "https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white">
<img src = "https://img.shields.io/badge/HTML-239120?style=for-the-badge&logo=html5&logoColor=white">
<img src = "https://img.shields.io/badge/CSS-239120?&style=for-the-badge&logo=css3&logoColor=white">
<img src = "https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white">
<img src = "https://img.shields.io/badge/chart.js-F5788D.svg?style=for-the-badge&logo=chart.js&logoColor=white">
<img src = "https://img.shields.io/badge/MySQL-00000F?style=for-the-badge&logo=mysql&logoColor=white">

<h2>Modules References</h2>
<h4>Core Functionalities</h4>
<a href = "https://flask.palletsprojects.com/en/3.0.x/">Flask</a> |
<a href = "https://pythonhosted.org/Flask-Mail/">Flask Mail</a> |
<a href = "https://dev.mysql.com/doc/connector-python/en/">MySQL Connector</a> |
<a href = "https://docs.python.org/3/library/os.html">OS</a> |
<a href = "https://docs.python.org/3/library/datetime.html">Datetime</a>
<a href = "https://tailwindcss.com/docs/installation">Tailwind CSS</a>
<h4>Hashing & security</h4>
<a href = "https://argon2-cffi.readthedocs.io/en/stable/">Argon2</a> |
<a href = "https://docs.python.org/3/library/base64.html">Base64</a>
<h4>Login Methods</h4>
<a href = "https://docs.authlib.org/en/latest/">Authlib's OAuth</a> |
<a href = "https://googleapis.github.io/google-api-python-client/docs/oauth.html#flow">Google's OAuth Flow</a>

<h2 id = "environmental-variables">Environmental Variables</h2>
<p>All the application's related variables such as the secret key, the <a href = "https://pythonhosted.org/Flask-Mail/">Flask Mail's configuration data</a> and <a href = "https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/authorizing-oauth-apps#web-application-flow">GitHub's OAuth URLs & app's secrets</a> are securely stored in the virtual environment (not included in this repository for security purposes since personal data are used).</p>
<p>Below a list and explanation of all the used virtual environment variables.</p>
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
<img src="https://github.com/mfacecchia/attendance-tracker/assets/86726458/a7bcf8b3-4055-4f8f-be83-1c3342a57a9b">

<h2 id = "app-routes">App Routes</h2>
<table>
  <tr>
    <th>Route</th>
    <th>Description</th>
  </tr>
  <tr>
    <td>/</td>
    <td>Landing page. Accessible to anyone who doesn't have an account or it's not logged in. If logged in, the user will be automatically redirected to the screening page.</td>
  </tr>
  <tr>
    <td>/login</td>
    <td>Login form. Outputs the form with Email and password input and validates the input passed through POST request. If already logged in, the user will be automatically redirected to the screening page. For more information about hashed password verification, <a href = "#hashing-methods">this section</a> will better explain the process.</td>
  </tr>
  <tr>
    <td>/forgot-password</td>
    <td>Outputs the form with Email input and sends an email to that adress with a reset password link. Accessible via the `/login` page. For more information about Email sending function and reset password link GET parameters, <a href = "#password-reset">this section</a> will better explain the process.</td>
  </tr>
  <tr>
    <td>/user/updatepassword</td>
    <td>Ouptuts the form with Password and Verify Password. Accessible via Email reset password link and after the very first login on the application.</td>
  </tr>
  <tr>
    <td>/user/updatepassword/verify</td>
    <td>Validates the already input password from `/user/updatepassword` form. For more information about password verification and hashing, <a href = "#hashing-methods">this section</a> will better explain the process.</td>
  </tr>
  <tr>
    <td>/auth/github</td>
    <td>Redirects to GitHub's OAuth App authorization. For more information about GitHub OAuth App Authorization process, please visit <a href = "https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/authenticating-to-the-rest-api-with-an-oauth-app">the official documentation</a>.</td>
  </tr>
  <tr>
    <td>/auth/github/callback</th>
    <td>GitHub OAuth App callback page, used to manage GitHub OAuth REST API return values. For more information about GitHub OAuth App Authorization process, please visit <a href = "https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/authenticating-to-the-rest-api-with-an-oauth-app">the official documentation</a>.</td>
  </tr>
  <tr id = "github-oauth-callback">
    <td>/auth/github/disconnect</td>
    <td>Removes GitHub Accoutn user id from the database</td>
  <tr>
    <td>/auth/google</td>
    <td>Redirects to Google's OAuth App Authorization. For more information about Google OAuth App Authorization process, please visit <a href = "https://developers.google.com/identity/protocols/oauth2">the official documentation</a>.</td>
  </tr>
  <tr>
    <td>/auth/google/callback</td>
    <td>Google OAuth App callback page, used to manage Google OAuth API return values. For more information about Google OAuth App Authorization process, please visit <a href = "https://developers.google.com/identity/protocols/oauth2">the official documentation</a>.</td>
  </tr>
  <tr>
    <td>/auth/google/disconnect</td>
    <td>Removes Google Account user id from the database</td>
  </tr>
  <tr>
    <td>/user</td>
    <td>User screening. Outputs user relates information such as name, role and last login time as well as a list of all upcoming lessons, a user creation form (ADMIN user role only), a lesson creation form (ADMIN and TEACHER user roles only), a course creation form (ADMIN user role only), a pie chart of attended/not attended lessons percentage (if the user role is STUDENT) or a bar chart of the total number of attendances subdivided per lesson date and course name in a chosen range of 7 days, 14 days or 30 days (if the user role is TEACHER or ADMIN). For more information about Chart generation, <a href = "#chart-generation">this section</a> will better explain the process. Accessible only if a <a href = "https://flask.palletsprojects.com/en/3.0.x/api/#sessions">session</a> is open, otherwise redirecting to login page with an error message.</td>
  </tr>
  <tr>
    <td>/user/create</td>
    <td>User creation function (only accessible to ADMIN user role).</td>
  </tr>
  <tr>
    <td>/lesson/create</td>
    <td>Lesson creation function (only accessible to ADMIN and TEACHER user roles).</td>
  </tr>
  <tr>
    <td>/lesson</td>
    <td>Lesson screening. Outputs the selected lesson name as well as a list of all enrolled students and a checkbox to record students attendance (only accessible to ADMIN and TEACHER user roles).</td>
  </tr>
  <tr>
    <td>/lesson/register-attendance</td>
    <td>Attendances registration function (only accessible to ADMIN and TEACHER user roles).</td>
  </tr>
  <tr>
    <td>/lesson/attendances</td>
    <td>Custom API that returns a JSON file about all lessons attendances count in a defined range. For more information about this API, <a href = "#lessons-attendances-count-api">this section</a> will better explain the process.</td>
  </tr>
  <tr>
    <td>/lessons/attendances/percentage</td>
    <td>Custom API that returns a JSON file about all lessons attendances/non attendances percentage rate in a defined range. For more information about this API, <a href = "#lessons-attendances-rate-api">this section</a> will better explain the process.</td>
  </tr>
  <tr>
    <td>/course/create</td>
    <td>Course creation function (only accessible to ADMIN user role)</td>
  </tr>
  <tr>
    <td>/user/list</td>
    <td>Outputs a list of all users registered in the platform with a button to update each user value such as name, surname, enrolled courses and more (only accessible to ADMIN user role).</td>
  </tr>
  <tr>
    <td>/user/select</td>
    <td>Outputs a form to update chosen user values such as name, surname, enrolled courses and more (only accessible to ADMIN user role).</td>
  </tr>
  <tr>
    <td>/user/update</td>
    <td>User update data function. Updates all chosen user data from the `/user/select` form.</td>
  </tr>
  <tr>
    <td>/user/logout</td>
    <td>Clears the user <a href = "https://flask.palletsprojects.com/en/3.0.x/api/#sessions">session</a> and logs the user out.</td>
  </tr>
  <tr>
    <td>/info</td>
    <td>Information page.</td>
  </tr>
  <tr>
    <td>/support</td>
    <td>Support page with contacts and FAQ.</td>
  </tr>
  <tr>
    <td>/terms-and-conditions</td>
    <td>Terms and conditions page randomly generated from <a href = "https://termly.io">Termly policies generator tool</a>.</td>
  </tr>
</table>

<h2 id = "hashing-methods">Hashing methods</h2>
<p>All user related sensitive data such as passwords are securely hashed and stored in the database using <a href = "https://en.wikipedia.org/wiki/Argon2">Argon2id algorithm</a>. To manage and verify such data, <a href = "https://argon2-cffi.readthedocs.io/en/stable/">Argon2-cffi</a> Python module is being used, in particular the `PasswordHasher` class and its relative methods <a href = "https://argon2-cffi.readthedocs.io/en/stable/api.html#argon2.PasswordHasher.verify">verify</a> for login and reset password verification functionalities and <a href = "https://argon2-cffi.readthedocs.io/en/stable/api.html#argon2.PasswordHasher.hash">hash</a> for user creation and reset password functionalities. Non matching passwords after the <a href = "https://argon2-cffi.readthedocs.io/en/stable/api.html#argon2.PasswordHasher.verify">verify</a> function is called are managed with Argon2 module built-in <a href = "https://argon2-cffi.readthedocs.io/en/stable/api.html#argon2.exceptions.VerifyMismatchError">VerifyMismatchError exception</a>.</p>

<h2 id = "functions">Functions</h2>
<h3>connectToDB()</h3>
<p>Starts a connection to the database with the given data through <a href = "https://dev.mysql.com/doc/connector-python/en/connector-python-api-mysqlconnection-connect.html">MySQLConnector.connect() function</a>. Connection not established is managed with <a href = "https://dev.mysql.com/doc/connector-python/en/connector-python-api-errors-error.html">MySQLConnector.Error</a> error.</p>
<p>Returns <a href = "https://dev.mysql.com/doc/connector-python/en/connector-python-example-connecting.html">MySQLConnection object</a> or `False` if the connection to Database fails for some reason.</p>

<h3>getCourses()</h3>
<p>Executes a simple `select` query on the database and returns all courses names and years.</p>
<p>Returns the formatted output of <a href = "https://dev.mysql.com/doc/connector-python/en/connector-python-api-mysqlcursor-execute.html">cursor.execute()</a>. For more information about query to list conversion, <a href = "#get-values-from-query">this section</a> will better explain the process.</p>

<h3 id = "get-values-from-query">getValuesFromQuery()</h3>
<p>Gets a <a href = "https://dev.mysql.com/doc/connector-python/en/connector-python-api-mysqlconnection-cursor.html">MySQLConnector cursor</a> as parameter and returns a list with dictionaries as items with cursor columns names as keys and obtained values as dictionary values. Briefly, this function will iterate though the entire cursor and create a dictionary for each query returned column. If the cursor is empty this function will return an empty list.</p>
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
<p>Programmatically updates user's last login time on database by executing an `update` SQL query on the database. The user is defined by session's userID value and the current time is obtained from <a href = "https://docs.python.org/3/library/datetime.html#datetime.date.today">date.today()</a> function.</p>
<p>Returns the formatted current date in `%d/%m/%Y` format by using <a href = "https://docs.python.org/3/library/datetime.html#datetime.date.strftime">date.strftime()</a> function.</p>

<h3>checkUserGithubConnection()</h3>
<p>Checks if the user has a linked Github account. The user is defined by session's userID value</p>
<p>Returns a boolean value corresponding `True` if the defined user has a linked Github Account or `False` if the Database's "githubID" field is empty</p>

<h3>linkGithubAccount()</h3>
<p>Updates user's "githubID" database column with the GitHub account id passed as function parameter from <a href = "#github-oauth-callback">GitHub OAuth API return values</a>. Before updating the column, a verifications is done; a <a href = "https://dev.mysql.com/doc/connector-python/en/connector-python-api-mysqlconnection-cursor.html">cursor</a> gets instantiated and checks if the obtained GitHub user id is already linked to an account with a simple `select` query. If the cursor's result contains no rows, then it is possible to update the user's `githubID` column and the session's related `githubConnected` value is set to `True`.</p>
<p>Returns `True` if the column is updated, otherwise `False` in all other cases.</p>

<h3>loginWithGithub()</h3>
<p>Looks for github user id obtained from the GitHub account id from <a href = "#github-oauth-callback">GitHub OAuth API return values</a> and executes a `select` query to obtain the relative user id from the database. If the user is found, a session gets created.</p>
<p>Returns `True` if the GitHub user id was found, otherwise `False`.</p>

<h3>validateFormInput()</h3>
<p>Validates form user input by checking if the input data is not an empty string.</p>
<p>Returns `True` if the passed string is empty, otherwise `False`</p>

<h3>getUsersList()</h3>
<p>Obtains all users from the database by executng a `select` query.</p>
<p>Returns the formatted output of <a href = "https://dev.mysql.com/doc/connector-python/en/connector-python-api-mysqlcursor-execute.html">cursor.execute()</a>. For more information about query to list conversion, <a href = "#get-values-from-query">this section</a> will better explain the process.</p>

<h3>getUserData()</h3>
<p>Gets all user related data by executing a `select` query. The user is defined by function parameter `uid`.</p>
<p>Returns the formatted output of <a href = "https://dev.mysql.com/doc/connector-python/en/connector-python-api-mysqlcursor-execute.html">cursor.execute()</a>. For more information about query to list conversion, <a href = "#get-values-from-query">this section</a> will better explain the process.</p>

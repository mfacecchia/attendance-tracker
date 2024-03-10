<img src = "https://github.com/mfacecchia/attendance-tracker/assets/86726458/0422693b-bbf6-4111-81d3-4ab67696a74a">
<h1 align = 'center'>Attendance Tracker</h1>
<p align = 'center'>Simple but useful app to easily record, manage and track teachers and students' attendances in schools.</p>

<h2>Table of Contents</h2>
<a href = "#built-in">Built in</a><br>
<a href = "#environmental-variables">Environmental Variables</a><br>
<a href = "#db-er">Database Entity Relationship model</a><br>
<a href = "#app-routes">App Routes</a>

<h2 id = "built-in">Built in</h2>
<img src = "https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white">
<img src = "https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white">
<img src = "https://img.shields.io/badge/HTML-239120?style=for-the-badge&logo=html5&logoColor=white">
<img src = "https://img.shields.io/badge/CSS-239120?&style=for-the-badge&logo=css3&logoColor=white">
<img src = "https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white">
<img src = "https://img.shields.io/badge/chart.js-F5788D.svg?style=for-the-badge&logo=chart.js&logoColor=white">

<h2>Modules References</h2>
<h4>Core Functionalities</h4>
<a href = "https://flask.palletsprojects.com/en/3.0.x/">Flask</a> |
<a href = "https://pythonhosted.org/Flask-Mail/">Flask Mail</a> |
<a href = "https://dev.mysql.com/doc/connector-python/en/">MySQL Connector</a> |
<a href = "https://docs.python.org/3/library/os.html">OS</a> |
<a href = "https://docs.python.org/3/library/datetime.html">Datetime</a>
<a href = "https://tailwindcss.com/docs/installation">Tailwind CSS</a>
<h4>Encryption & security</h4>
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
    <td>Login form. Outputs the form with Email and password input and validates the input passed through POST request. If already logged in, the user will be automatically redirected to the screening page. For more information about encrypted password verification, <a href = "#encryption-methods">this section</a> will better explain the process.</td>
  </tr>
  <tr>
    <td>/forgot-password</td>
    <td>Outputs the form with Email input and sends an email to that adress with a reset password link. Accessible via the `/login` page.</td>
  </tr>
  <tr>
    <td>/user/updatepassword</td>
    <td>Ouptuts the form with Password and Verify Password. Accessible via Email reset password link and after the very first login on the application.</td>
  </tr>
  <tr>
    <td>/user/updatepassword/verify</td>
    <td>Validates the already input password from `/user/updatepassword` form. For more information about password verification and encryption, <a href = "#encryption-methods">this section</a> will better explain the process.</td>
  </tr>
  <tr>
    <td>/auth/github</td>
    <td>Redirects to GitHub's OAuth App authorization. For more information about GitHub OAuth App Authorization process, please visit <a href = "https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/authenticating-to-the-rest-api-with-an-oauth-app">the official documentation</a>.</td>
  </tr>
  <tr>
    <td>/auth/github/callback</th>
    <td>GitHub OAuth App callback page, used to manage GitHub OAuth REST API return values. For more information about GitHub OAuth App Authorization process, please visit <a href = "https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/authenticating-to-the-rest-api-with-an-oauth-app">the official documentation</a>.</td>
  </tr>
  <tr>
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
  <tr>
    <td>/docs</td>
    <td>Documentation page. Link to this README file</td>
  </tr>
</table>

<img src = "https://github.com/mfacecchia/attendance-tracker/assets/86726458/0422693b-bbf6-4111-81d3-4ab67696a74a">
<h1 align = 'center'>Attendance Tracker</h1>
<p align = 'center'>Simple but useful app for managing teachers and students attendances in a school.</p>

<h2>Table of Contents</h2>
<a href = "#built-in">Built in</a><br>
<a href = "#environmental-variables">Environmental Variables</a><br>
<a href = "#db-er">Database Entity Relationship model</a>

<h2 id = "built-in">Built in</h2>
<img src = "https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white">
<img src = "https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white">
<img src = "https://img.shields.io/badge/HTML-239120?style=for-the-badge&logo=html5&logoColor=white">
<img src = "https://img.shields.io/badge/CSS-239120?&style=for-the-badge&logo=css3&logoColor=white">
<img src = "https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white">

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

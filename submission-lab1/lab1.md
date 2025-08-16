Lab 1 Submission
Setup Instructions

Clone the repo: git clone https://github.com/hervenoubs/mooli-django-project.git
Navigate to project: cd mooli-django-project/the_mooli_project
Create a virtual environment: python3 -m venv env
Activate: source env/bin/activate (Mac/Linux) or env\Scripts\activate (Windows)
Install dependencies: pip install -r requirements.txt
Ensure MySQL is running: mysql.server start
Create a MySQL database named mooli_project_db in phpMyAdmin
Update .env with MySQL credentials
Run migrations: python3 manage.py migrate
Load fixtures: python3 manage.py loaddata initial_data
Compile translations: python3 manage.py compilemessages
Collect static files: python3 manage.py collectstatic
Run server: python3 manage.py runserver
Open http://127.0.0.1:8000/

Features

Converted 4 Mooli pages: Dashboard (index.html), Login, Register, Forgot Password.
Email-based login system with custom user model (CustomUser).
User Profile and Company models (Many-to-One).
Profile switcher in sidebar (mimics Gmail multi-profile).
Multilingual support (English + French) with language stored in UserProfile.
Initial data seeding with HelloWorld Company and test user.
MySQL database backend configured with phpMyAdmin.
Fixed duplicate message definitions in django.po.
Fixed TemplateSyntaxError for get_current_language and static tag in base.html.
Fixed ImproperlyConfigured error by setting STATIC_ROOT.
Fixed VariableDoesNotExist error by restricting dashboard access.
Fixed 404 error by setting LOGIN_URL = 'login'.
Fixed login page loader issue by adding fallback CSS/JS and removing vivify animation.

Screenshots

Dashboard: [Insert screenshot]
Login: [Insert screenshot]
Register: [Insert screenshot]
Forgot Password: [Insert screenshot]
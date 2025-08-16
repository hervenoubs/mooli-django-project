Mooli Django Project
A Django-based admin dashboard built with the Mooli Bootstrap 4x template, featuring email-based authentication, multilingual support (English and French), and company profile switching.
Features

Pages: Dashboard, Login, Register, Forgot Password.
Authentication: Email-based login using a custom user model (CustomUser).
Models: CustomUser, Company, UserProfile (Many-to-One relationship).
Profile Switching: Switch between companies in the sidebar (similar to Gmail profiles).
Multilingual Support: English and French translations with language stored in UserProfile.
Database: MySQL backend with phpMyAdmin integration.
Static Files: Mooli template assets (Bootstrap, Font Awesome, Chartist, etc.).
Initial Data: Fixture with a test user and company (test@example.com, HelloWorld Company).

Prerequisites

Python 3.9.6
MySQL
phpMyAdmin
Git

Setup Instructions

Clone the Repository:
git clone https://github.com/hervenoubs/mooli-django-project.git
cd mooli-django-project/the_mooli_project


Create and Activate Virtual Environment:
python3 -m venv env
source env/bin/activate  # Mac/Linux
# env\Scripts\activate  # Windows


Install Dependencies:
pip install -r requirements.txt


Configure Environment Variables:Create a .env file in the project root:
SECRET_KEY=your-secret-key
DEBUG=True
DB_NAME=mooli_project_db
DB_USER=root
DB_PASSWORD=your-mysql-password
DB_HOST=localhost
DB_PORT=3306


Apply Migrations:
python3 manage.py migrate

Verify Fixtures:
python3 manage.py shell
from django.contrib.auth.hashers import make_password
print(make_password("your-own-password"))

Load Initial Data:
python3 manage.py loaddata initial_data


Compile Translations:
python3 manage.py compilemessages


Collect Static Files:
python3 manage.py collectstatic


Run the Development Server:
python3 manage.py runserver


Access the Application:

Open http://127.0.0.1:8000/.
Login: test@example.com with the password from initial_data.json.
Admin: http://127.0.0.1:8000/admin/ (create a superuser if needed: python3 manage.py createsuperuser).



URLs

Dashboard: /
Login: /login/
Logout: /logout/
Register: /register/
Forgot Password: /forgot-password/
Set Language: /set-language/?lang=en or /set-language/?lang=fr
Switch Company: /switch-company/<company_id>/

Debugging Tips

Static Files: Ensure collectstatic ran and staticfiles/ contains assets.
Translations: Verify django.mo in locale/fr/LC_MESSAGES/ and LocaleMiddleware in settings.py.
Database: Check MySQL connection and tables in phpMyAdmin.
JavaScript Errors: Use Developer Tools (F12) → Console tab to debug.

Known Issues and Fixes

Duplicate Translations: Removed duplicate msgid in django.po.
Template Errors: Fixed get_current_language and static tag issues in base.html.
Static Files: Set STATIC_ROOT and ran collectstatic.
Authentication: Added LOGIN_URL = 'login' and restricted dashboard access.
Loader Issue: Added fallback CSS/JS to hide the page loader.

Repository Structure

the_mooli_project/: Django project directory.
mooli_app/: Main app with models, views, and URLs.
static/: Development static files (Mooli assets).
staticfiles/: Collected static files for deployment.
templates/: HTML templates (base.html, login.html, etc.).
locale/: Translation files (django.po, django.mo).
submission-lab1/: Lab submission (lab1.md).

Screenshots

Dashboard: [Add screenshot]
Login: [Add screenshot]
Register: [Add screenshot]
Forgot Password: [Add screenshot]

Next Steps

Implement registration and password reset logic in views.py.
Add dashboard content (e.g., charts, tables).
Proceed to Lab 2 (AI chatbot with AWS Bedrock).
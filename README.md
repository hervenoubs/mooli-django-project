Mooli Django Project
A Django-based admin dashboard built with the Mooli Bootstrap 4x template, featuring email-based authentication, multilingual support, and company profile switching.
Features

Pages: Dashboard, Login, Register, Forgot Password.
Authentication: Email-based login with custom user model (CustomUser).
Registration: First name, last name, email, password; username from email; activation email with 1-hour expiry.
Password Reset: Gmail SMTP for reset emails.
Dashboard: Displays first name, logout, company switcher (Gmail-style), language switcher (English/French).
Models: CustomUser, Company, UserProfile (ManyToMany for companies, ForeignKey for current company).
Multilingual Support: English and French with language stored in UserProfile.
Database: MySQL backend with phpMyAdmin.
Static Files: Mooli template assets (Bootstrap, Font Awesome, etc.).
Initial Data: Test user and company (test@example.com, HelloWorld Company).

Prerequisites

Python 3.9.6
MySQL
phpMyAdmin
Git
Gmail account with App Password for SMTP

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


Configure Environment Variables:Create a .env file:
SECRET_KEY=your-secret-key
DEBUG=True
DB_NAME=mooli_project_db
DB_USER=root
DB_PASSWORD=your-mysql-password
DB_HOST=localhost
DB_PORT=3306
EMAIL_HOST_USER=yourgmail@gmail.com
EMAIL_HOST_PASSWORD=your_app_password


Apply Migrations:
python3 manage.py makemigrations
python3 manage.py migrate


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
Login: test@example.com with password from initial_data.json.
Admin: http://127.0.0.1:8000/admin/ (create superuser: python3 manage.py createsuperuser).



URLs

Dashboard: /
Login: /login/
Logout: /logout/
Register: /register/
Forgot Password: /forgot-password/
Password Reset: /reset-password/, /reset/<uidb64>/<token>/, etc.
Activate Account: /activate/<uidb64>/<token>/
Set Language: /set-language/?lang=en or /set-language/?lang=fr
Switch Company: /switch-company/<company_id>/

Debugging Tips

Static Files: Verify staticfiles/ after collectstatic.
Translations: Check locale/fr/LC_MESSAGES/django.mo and LocaleMiddleware.
Database: Confirm MySQL tables in phpMyAdmin.
Email: Test Gmail SMTP in shell.
JavaScript Errors: Use Developer Tools → Console.

Known Issues and Fixes

Fixed loader issue with auth_base.html.
Fixed read-only form by updating CustomLoginForm.
Separated forms into forms.py.
Configured Gmail SMTP for email sending.

Repository Structure

the_mooli_project/: Django project directory.
mooli_app/: App with models, views, forms, URLs.
static/: Mooli assets.
staticfiles/: Collected static files.
templates/: HTML templates (auth_base.html, base.html, etc.).
locale/: Translation files (django.po, django.mo).
submission-lab1/: Lab submission (lab1.md).

Screenshots

Dashboard: [Add screenshot]
Login: [Add screenshot]
Register: [Add screenshot]
Forgot Password: [Add screenshot]

Next Steps

Proceed to Lab 2 (AI chatbot with AWS Bedrock).

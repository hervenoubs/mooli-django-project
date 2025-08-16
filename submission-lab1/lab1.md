Lab 1 Submission
Setup Instructions

Clone the repo: git clone https://github.com/hervenoubs/mooli-django-project.git
Navigate to project: cd mooli-django-project/the_mooli_project
Create virtual environment: python3 -m venv env
Activate: source env/bin/activate (Mac/Linux) or env\Scripts\activate (Windows)
Install dependencies: pip install -r requirements.txt
Create and start MySQL database mooli_project_db in phpMyAdmin
Update .env with MySQL and Gmail SMTP credentials
Run migrations: python3 manage.py makemigrations && python3 manage.py migrate
Load fixtures: python3 manage.py loaddata initial_data
Compile translations: python3 manage.py compilemessages
Collect static files: python3 manage.py collectstatic
Run server: python3 manage.py runserver
Open http://127.0.0.1:8000/

Features

Converted Mooli pages: Dashboard, Login, Register, Forgot Password.
Email-based login with CustomUser.
Registration with first name, last name, email, password; username from email; activation email (1-hour expiry).
Password reset via Gmail SMTP.
Dashboard displays first name, logout, company/language switchers.
Models: CustomUser, Company, UserProfile (ManyToMany companies, ForeignKey current_company).
Multilingual support (English/French) stored in UserProfile.
MySQL backend with phpMyAdmin.
Fixed loader issue, read-only form, separated forms into forms.py.

Screenshots

Dashboard: [Insert screenshot]
Login: [Insert screenshot]
Register: [Insert screenshot]
Forgot Password: [Insert screenshot]

Lab 1 Submission
Setup Instructions

Clone the repo: git clone https://github.com/yourusername/mooli-django-project.git
Navigate to project: cd mooli-django-project/the_mooli_project
Create a virtual environment: python3 -m venv env
Activate: source env/bin/activate (Mac/Linux) or env\Scripts\activate (Windows)
Install dependencies: pip install -r requirements.txt
Create a MySQL database named mooli_project_db in phpMyAdmin
Update settings.py with your MySQL credentials
Run migrations: python3 manage.py migrate
Load fixtures: python3 manage.py loaddata initial_data
Run server: python3 manage.py runserver
Open http://127.0.0.1:8000/

Features

Converted 4 Mooli pages: Dashboard (index.html), Login, Register, Forgot Password.
Email-based login system with custom user model.
User Profile and Company models (Many-to-One).
Profile switcher in sidebar (mimics Gmail multi-profile).
Multilingual support (English + French) with language stored in UserProfile.
Initial data seeding with HelloWorld Company and test user.
MySQL database backend configured with phpMyAdmin.

Screenshots

Dashboard: [Insert screenshot]
Login: [Insert screenshot]
Register: [Insert screenshot]
Forgot Password: [Insert screenshot]
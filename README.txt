Installation
==============
    Target Platform
    ----------------
        - Windows 7
        - Python 3.4.3 installed
        - Django 1.9.1 installed
        - Sqlite 3.8

    Pre-Config
    ----------
        - Python 3.4.3 executable exists in path
        - Pip is installed and exists in path

    Installation Steps
    ------------------
        - Unzip healthnet
        - Open a cmd window (anywhere) and type "pip install django==1.9.1"

Running
=======
    Starting The System
    --------------------
        - Open a cmd window in the healthnet root directory, it will be the folder containing manage.py
        - Type "python manage.py runserver"
        - In a web browser navigate to localhost:8000/

    Resetting the database
    ----------------------
        - Open a cmd window in the healthnet root directory, the same directory as manage.py
        - Type "python manage.py shell < build_test_db.py"

    Default Users
    --------------
        These uses can be used to test the system
        - Doctor Strange, username: drstrange and password: pass
        - Nurse Normal, username: nursenormal and password: pass
        - Patient Zero, username: patientzero and password: pass

    Creating an Admin account
    -------------------------
        - Open a cmd window in the healthnet root directory, it will be the folder containing manage.py
        - Type "python manage.py createsuperuser"
        - Follow the prompts
        - Once done you can login to the admin after starting the system by navigating to localhost:8000/admin

    Known Bugs
    ----------
        - When filling out any forms, if a field is left blank and the form is submitted an error page is displayed
        - If a user doesn't fill out the hospital during registration it results in an unknown user state and various features stop working

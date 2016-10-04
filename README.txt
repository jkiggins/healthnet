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

    Installation Steps
    ------------------
        - Unzip healthnet in target folder
	- Open a cmd window in the healnet root directory, it will be folder containing manage.py
	- type in command "python manage.py makemigrations" wait for it to finish
	- type in command "python manage.py migrate" wait for it to finish
	- type in command "python manage.py shell < build_test_db.py" this creates default/basic users

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
	- Clicking on Doctor link in Profile of Patient causes error
	- There can be overlapping events with different people
	
    Features Missing in Release-1
    -----------------------------
	-Month, Week, Day view for Patient, Nurse, and Doctor respectfully
	-Patient emerency contact can't be linked to another user in system
	-Trusted nurses aren't implemeneted

    Features in Release-1
    ---------------------
	-Registration of patients with proof of insurance
	-Editing the profile of a patient, and can only be editied by that patient
	-Event creation with events showing up on affecting users' calendars
	-Viewing an event and it's details
	-Doctors and Patients can delete an event
	-Nurses can create events between different doctors and patients
	-Events won't form when the doctor isn't located at location/hospital
	-Logs created for various actions preformed by users
	-Logs can be viewed by admin
	-Successful login of users registered in system
	-Doctor viewing all of their patients
	-EMR viewing and vital history
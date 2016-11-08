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
        Doctor - Doctor Strange, username: drstrange and password: pass
        Nurse - Nurse Normal, username: nursenormal and password: pass
        Patient- Patient Zero, username: patientzero and password: pass
	Hospital Administrator - Kid Cudi, username: cudi and password: pass

    Creating an Admin account
    -------------------------
        - Open a cmd window in the healthnet root directory, it will be the folder containing manage.py
        - Type "python manage.py createsuperuser"
        - Follow the prompts
        - Once done you can login to the admin after starting the system by navigating to localhost:8000/admin
 
    Known Bugs R-2 Beta
    -------------------
	-


    Missing Features R-2 Beta
    -------------------------
	- Messaging is not yet implemented
	- Notifications are not yet implemented


    Released Features R-2 Beta
    --------------------------
	- Addition/removal of perscriptions by doctors to patients records
	- Nurses can view patient perscritions
	- Doctors can view and edit the Patient EMR
	- Patients are able to view test results only after doctors have released them
	- User Activity is logged and The hosptial Admin can view and search through it by date/time. 
	- A doctor or nurse can admit a patient to the hospital and a doctor can discharge him/her
	- Administrators/Doctors can transfer patients to other hosptials
	- Doctors can upload test results for Patients (NOTE: Must pip install pillow!) 
	- Exporting and importing CSV data for EMR information

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
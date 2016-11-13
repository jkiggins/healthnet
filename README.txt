__/\\\________/\\\________________________________/\\\\\\___________________/\\\_________        
 _\/\\\_______\/\\\_______________________________\////\\\__________________\/\\\_________       
  _\/\\\_______\/\\\__________________________________\/\\\________/\\\______\/\\\_________      
   _\/\\\\\\\\\\\\\\\_____/\\\\\\\\___/\\\\\\\\\_______\/\\\_____/\\\\\\\\\\\_\/\\\_________     
    _\/\\\/////////\\\___/\\\/////\\\_\////////\\\______\/\\\____\////\\\////__\/\\\\\\\\\\__    
     _\/\\\_______\/\\\__/\\\\\\\\\\\____/\\\\\\\\\\_____\/\\\_______\/\\\______\/\\\/////\\\_   
      _\/\\\_______\/\\\_\//\\///////____/\\\/////\\\_____\/\\\_______\/\\\_/\\__\/\\\___\/\\\_  
       _\/\\\_______\/\\\__\//\\\\\\\\\\_\//\\\\\\\\/\\__/\\\\\\\\\____\//\\\\\___\/\\\___\/\\\_ 
        _\///________\///____\//////////___\////////\//__\/////////______\/////____\///____\///__
	________________/\\\\\_____/\\\____________________________________________                      
	 _______________\/\\\\\\___\/\\\____________________________________________                     
	  ______/\\\_____\/\\\/\\\__\/\\\____________________/\\\___________/\\\_____                    
	   _____\/\\\_____\/\\\//\\\_\/\\\_____/\\\\\\\\___/\\\\\\\\\\\_____\/\\\_____                   
	    __/\\\\\\\\\\\_\/\\\\//\\\\/\\\___/\\\/////\\\_\////\\\////___/\\\\\\\\\\\_                  
	     _\/////\\\///__\/\\\_\//\\\/\\\__/\\\\\\\\\\\_____\/\\\______\/////\\\///__                 
	      _____\/\\\_____\/\\\__\//\\\\\\_\//\\///////______\/\\\_/\\______\/\\\_____                
	       _____\///______\/\\\___\//\\\\\__\//\\\\\\\\\\____\//\\\\\_______\///______               
	        _______________\///_____\/////____\//////////______\/////__________________    


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
	- type in command "pip install pillow" wait for it to finish
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
    -------------
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
	- When selecting a emergency contact, if you select a emergency contact that someone else has already selected, an integrety error is thrown because of a unique field.
	- User clicks on event in calendar.io, goes to edit event, changes date to past, it saves (shouldn't allow for previous date change)
	- New nurse can't "Create Event"
	- Nurse can't edit their own profile
	- New nurse, on search healthnet, check mark doctors, click search, no doctors displayed
	- Patient Registering can select a doctor that's not approved (filter for approval, like patient cap)
	- patient can reference self as a emergency contact
	- Patient registering can pick a hospital that a doctor isn't associated with
	- Doctor editing event can change hospitals
	- Doctor editing event can change patient relating to event
	- Doctor edits an event, changes duration, saves, goes back to edit the event, the duration is reset to 30 mins
	- Users (except admin) shouldn't be able to edit past events
	- Doctor can't access Patient via Doctor's profile
	- New registered doctor, with no patients, can go to create event and select a patient from his hospital and make an appointment with said patient (should only be allowed to make an appointment with patient connected with him)
	- Doctor at hospital A goes to search healthnet, clicks on patient, nothing shows up
	- new patient makes basic profile, hospital doctor selection, then goes to EMR 
	- when you hit save on some fields, it is saved data but it is not visible.

    Missing Features R-2 Beta
    -------------------------
	- Messaging is not yet implemented
	- Notifications are not yet implemented
	- Doctor Patient Cap is unimplemented

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


Cheers,
     _____                                    
 ___|__   |__  ______  ____    ____    __     
|_    _|     ||   ___||    \  |    \  /  |    
 |    |      ||   ___||     \ |     \/   |    
 |____|    __||______||__|\__\|__/\__/|__|    
    |_____|                                   
     _____                                    
  __|_    |__  ____    _____  __   _  ____    
 |    \      ||    |  |     ||  |_| ||    \   
 |     \     ||    |_ |    _||   _  ||     \  
 |__|\__\  __||______||___|  |__| |_||__|\__\ 
    |_____|                                   
                  
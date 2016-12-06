__/\\\________/\\\________________________________/\\\\\\___________________/\\\_________        
 _\/\\\_______\/\\\_______________________________\////\\\__________________\/\\\_________       
  _\/\\\_______\/\\\__________________________________\/\\\________/\\\______\/\\\_________      
   _\/\\\\\\\\\\\\\\\_____/\\\\\\\\___/\\\\\\\\\_______\/\\\_____/\\\\\\\\\\\_\/\\\_________     
    _\/\\\/////////\\\___/\\\/////\\\_\////////\\\______\/\\\____\////\\\////__\/\\\\\\\\\\__    
     _\/\\\_______\/\\\__/\\\\\\\\\\\____/\\\\\\\\\\_____\/\\\_______\/\\\______\/\\\/////\\\_   
      _\/\\\_______\/\\\_\//\\///////____/\\\/////\\\_____\/\\\_______\/\\\_/\\__\/\\\___\/\\\_  
       _\/\\\_______\/\\\__\//\\\\\\\\\\_\//\\\\\\\\/\\__/\\\\\\\\\____\//\\\\\___\/\\\___\/\\\_ 
        _\///________\///____\//////////___\////////\//__\/////////______\/////____\///____\///__
	 _____________________/\\\\\_____/\\\_____________________________________________________       
	  ____________________\/\\\\\\___\/\\\_____________________________________________________                     
	   ___________/\\\_____\/\\\/\\\__\/\\\____________________/\\\___________/\\\______________                    
	    __________\/\\\_____\/\\\//\\\_\/\\\_____/\\\\\\\\___/\\\\\\\\\\\_____\/\\\______________                   
	     _______/\\\\\\\\\\\_\/\\\\//\\\\/\\\___/\\\/////\\\_\////\\\////___/\\\\\\\\\\\__________                  
	      ______\/////\\\///__\/\\\_\//\\\/\\\__/\\\\\\\\\\\_____\/\\\______\/////\\\///___________                 
	       __________\/\\\_____\/\\\__\//\\\\\\_\//\\///////______\/\\\_/\\______\/\\\______________                
	        __________\///______\/\\\___\//\\\\\__\//\\\\\\\\\\____\//\\\\\_______\///_______________               
	         ____________________\///_____\/////____\//////////______\/////___________________________    


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
===============
	TurnKey (Auto run)
	----------------------------
	-Unzip healthnet in target folder
	-double click on turnkey.bat
	Manual installation
	------------------------
        - Unzip healthnet in target folder
	- Open a cmd window in the healnet root directory, it will be folder containing manage.py
	- type in command "pip install pillow" wait for it to finish
	- type in command "python manage.py makemigrations" wait for it to finish
	- type in command "python manage.py migrate" wait for it to finish
	- type in command "python manage.py shell < build_test_db.py" this creates default/basic users


Running
=======
    Starting The System Automatic
    --------------------
        - Go to healthnet root directory
        - run turnkey.bat
        - In a web browser navigate to localhost:80/
    Starting The System Manually
    --------------------
        - Open a cmd window in the healthnet root directory, it will be the folder containing manage.py
        - Type "python manage.py runserver"
        - In a web browser navigate to localhost:8000/


    Resetting the database
    ------------------------------
        - Open a cmd window in the healthnet root directory, the same directory as manage.py
        - Type "python manage.py shell < build_test_db.py"


    Default Users
    ------------------
        These uses can be used to test the system
        Doctor - Doctor Strange, username: drstrange and password: pass
	- Doctor Normal, username: drnormal and password: pass
        Nurse - Nurse Normal, username: nursenormal and password: pass
        Patient- Patient Zero, username: patientzero and password: pass
	- Patient One, username: patientone and password: pass
	Hospital Administrator - Kid Cudi, username: cudi and password: pass


    Creating an Admin account
    -------------------------
        - Open a cmd window in the healthnet root directory, it will be the folder containing manage.py
        - Type "python manage.py createsuperuser"
        - Follow the prompts
        - Once done you can login to the admin after starting the system by navigating to localhost:8000/admin
 
    Known Bugs R-2
    -------------------
	- Doctor edits an event, changes duration, saves, goes back to edit the event, the duration is reset to 30 mins
	- New registered doctor, with no patients, can go to create event and select a patient from his hospital and make an appointment with said patient (should only be allowed to make an appointment with patient connected with him)
	- during patient registration incorrect password matching or taken username will redirect to insurance # instead of remaining on page
	- Patient editing profile can change email to be improper
	- Patient leaving editing profile without saving should prompt a warning message
	- User creating an event that clicks away should prompt a warning message
	- Admin discharging or admitting a patient Can get to the point but doesn't allow for "saving." says hospital field is needed but admin cannot edit it


    Missing Features R-2
    -----------------------------
            - CSV EMR importing/exporting
            - Specific User Interface options


    Released Features R-2 Beta
    --------------------------
	- Addition/removal of prescriptions by doctors to patients records
	- Nurses can view patient prescriptions
	- Doctors can view and edit the Patient EMR
	- Patients are able to view test results only after doctors have released them
	- User Activity is logged and The hospital Admin can view and search through it by date/time. 
	- A doctor or nurse can admit a patient to the hospital and a doctor can discharge him/her
	- Administrators/Doctors can transfer patients to other hospitals
	- Doctors can upload test results for Patients (NOTE: Must pip install pillow!) 
	- Exporting and importing CSV data for EMR information


    Features in Release-1
    ---------------------
	-Registration of patients with proof of insurance
	-Editing the profile of a patient, and can only be edited by that patient
	-Event creation with events showing up on affecting users' calendars
	-Viewing an event and it's details
	-Doctors and Patients can delete an event
	-Nurses can create events between different doctors and patients
	-Events won't form when the doctor isn't located at location/hospital
	-Logs created for various actions performed by users
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
                  
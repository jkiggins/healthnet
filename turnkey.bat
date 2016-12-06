@echo off

cd HealthNet
python manage.py makemigrations user
python manage.py migrate user

python manage.py makemigrations emr
python manage.py migrate emr

python manage.py makemigrations
python manage.py migrate

pip install Pillow --user

python manage.py db_beta

python manage.py createsuperuser

python manage.py runserver 127.0.0.1:80
@echo off

cd HealthNet
python manage.py makemigrations
python manage.py migrate

python manage.py makemigrations user
python manage.py migrate

python manage.py makemigrations emr
python manage.py migrate

python manage.py db_beta

python manage.py runserver 127.0.0.1:80
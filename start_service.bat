@echo off
cd /d D:\brototype\2nd project\HomiGo\backend

call ..\virtualenv\Scripts\activate

start cmd /k "..\virtualenv\Scripts\activate && python manage.py runserver"
start cmd /k "..\virtualenv\Scripts\activate && celery -A backend worker --loglevel=info --pool=solo"

echo Both celery and server has been started in separate terminals.
pause

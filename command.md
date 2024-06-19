1. >> pipenv shell
2. >> pipenv install
3. create your own .env which contains:
DEBUG=
SECRET_KEY=
ALLOWED_HOSTS=
DB_NAME=
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=
GDAL_LIBRARY_PATH=

*** Have to download OSGeo4W and include the path 
Ex: GDAL_LIBRARY_PATH=C:\OSGeo4W\bin\gdal309
>> python manage.py runserver
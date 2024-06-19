# install all deps in the venv
python3 -m pip install -r requirements.txt

python3 manage.py makemigrations --noinput
python3 manage.py migrate --noinput

# collect static files using the Python interpreter from venv
python3 manage.py collectstatic --noinput


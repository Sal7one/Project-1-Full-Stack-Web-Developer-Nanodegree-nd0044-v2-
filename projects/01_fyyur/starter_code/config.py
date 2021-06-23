import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database


# TODO IMPLEMENT DATABASE URL

# Password needed for windows to run local db
SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:aa050@localhost:5432/fyyur'

# Disable warning
SQLALCHEMY_TRACK_MODIFICATIONS = False
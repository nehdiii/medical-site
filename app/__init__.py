import os.path
import dash
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

#Flask-Login provides user session management for Flask.
# It handles the common tasks of logging in, logging out, and remembering your users’ sessions over extended periods of time.
#loginManager class is for login managment
# Store the active user’s ID in the session, and let you log them in and out easily.
app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
# data base instance


db = SQLAlchemy(app)
bcrypt=Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login' #'login' hia function name of our route
login_manager.login_message_category = 'info' # the style we want to display the msg

from app import routes
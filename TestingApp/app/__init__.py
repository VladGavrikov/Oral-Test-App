from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'

app.config.update(dict(
    DEBUG = True,
    MAIL_SERVER = 'smtp.sendgrid.net',
    MAIL_PORT = 587,
    MAIL_USE_TLS = True,
    MAIL_USE_SSL = False,
    MAIL_SUPPRESS_SEND=False,
    TESTING=False,
    MAIL_USERNAME = 'apikey',
    MAIL_PASSWORD = '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',
    #CITS3200Group15CITS3200Group15
	MAIL_DEFAULT_SENDER = 'speakfluentapp@gmail.com',
))

mail = Mail(app)
from app import routes, models, errors


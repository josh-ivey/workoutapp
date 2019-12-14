from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
import os

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
app.config["FACEBOOK_OAUTH_CLIENT_ID"] = "737868353346462"
app.config["FACEBOOK_OAUTH_CLIENT_SECRET"] = "c0acc58aff5c6f4d3e687346b4060e5a"

app.secret_key = "some_secret_key"

db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

from my_app.auth.views import auth, facebook_blueprint
app.register_blueprint(auth)
app.register_blueprint(facebook_blueprint)

db.create_all()

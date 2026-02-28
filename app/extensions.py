from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask_caching import Cache
from flask_login import LoginManager
from flask_migrate import Migrate
db= SQLAlchemy()
socketio= SocketIO()
cache= Cache()
login_manager= LoginManager()
migrate= Migrate()
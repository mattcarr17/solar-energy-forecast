import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import timedelta
from apscheduler.schedulers.background import BackgroundScheduler
import json
import pandas as pd
import requests


app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('config.py')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)


from .views import views
app.register_blueprint(views)

from .scheduler import scheduler
scheduler.start()

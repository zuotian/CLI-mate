"""
@organization: Leiden University Medical Center (LUMC)
@author: Zuotian Tatum
@contact: z.tatum@lumc.nl
"""

from flask import Flask
from flask.ext.login import LoginManager
from flask.ext.mongoengine import MongoEngine
import os


app = Flask(__name__)
app.config.from_pyfile('../climate.cfg')

# setup database
db = MongoEngine(app)

# setup authentication
login_manager = LoginManager()
login_manager.init_app(app)

from . import views
"""
@organization: Leiden University Medical Center (LUMC)
@author: Zuotian Tatum
@contact: z.tatum@lumc.nl
"""

from flask import Flask
from flask.ext.mongoengine import MongoEngine
import os


app = Flask(__name__)
app.config.from_pyfile('../climate.cfg')
db = MongoEngine(app)

from . import views
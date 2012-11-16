"""
@organization: Leiden University Medical Center (LUMC)
@author: Zuotian Tatum
@contact: z.tatum@lumc.nl
"""

from flask import Flask
from flask.ext.mail import Mail
from flask.ext.mongoengine import MongoEngine


app = Flask(__name__)
app.config.from_pyfile('../climate.cfg')

# setup database
db = MongoEngine(app)

# setup mail for security
mail = Mail(app)
app.extensions['mail'] = mail

from . import views
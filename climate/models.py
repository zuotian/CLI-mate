"""
@organization: Leiden University Medical Center (LUMC)
@author: Zuotian Tatum
@contact: z.tatum@lumc.nl
"""

from climate import db
import datetime

class Parameter(db.EmbeddedDocument):
    name = db.StringField(required=True, max_length=50)
    type = db.StringField(required=True, max_length=50,
                          choices=[(x, x) for x in ["None", "integer", "float", "string", "input", "output", "stdin", "stdout", "stderr"]])
    arg = db.StringField(max_length=2)
    arg_long = db.StringField(max_length=50)
    value = db.StringField(max_length=50)
    format = db.StringField(max_length=50)
    rank = db.IntField()

    choices = db.StringField(max_length=50)
    label = db.StringField(max_length=50)
    description = db.StringField(max_length=50)

    display = db.StringField(choices=[(x, x) for x in ["show", "hide", "show in advanced"]])
    min_occurrence = db.StringField()
    max_occurrence = db.StringField()

class ToolRequirement(db.EmbeddedDocument):
    type = db.StringField(choices=[(x, x) for x in ["binary", "python-module"]])
    name = db.StringField(max_length=50),
    location = db.StringField(max_length=200)

class Tool(db.Document):
    name = db.StringField(required=True, max_length=50)
    binary = db.StringField(required=True, max_length=50)
    description = db.StringField(max_length=100)
    owner = db.StringField(max_length=50)
    owner = db.StringField(max_length=50)
    email = db.EmailField()
    version = db.StringField(max_length=50)
    version = db.StringField(max_length=50)
    help = db.StringField()

    os = db.StringField(choices=[(x, x) for x in ["Linux"]])
    interpreter = db.StringField(choices=[(x, x) for x in ["(binary)", "bash", "python", "perl", "java"]])
    grid_access_type = db.StringField(choices=[(x, x) for x in ["-", "LFN", "URL"]])
    grid_access_location = db.StringField(max_length=250)

    parameters = db.ListField(db.EmbeddedDocumentField('Parameter'))
    requirements = db.ListField(db.EmbeddedDocumentField('ToolRequirement'))

########################################################################################################################
# database models with SQLAlchemy

#from flask.ext.sqlalchemy import SQLAlchemy
#db = SQLAlchemy(app)
#
#class User(db.Model):
#    __tablename__ = 'users'
#
#    id = db.Column(db.Integer, primary_key=True)
#    name = db.Column(db.String(60), nullable=False)
#    password = db.Column(db.String(128))
#    email = db.Column(db.String(60))
#
#    # tools = db.relationship('Tool', backref='user', lazy='dynamic')
#
#class ToolDefinition(db.Model):
#    __tablename__ = 'tool_definitions'
#
#    id = db.Column(db.Integer, primary_key=True)
#    name = db.Column(db.String(60), nullable=False)
#    # created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
#    created = db.Column(db.DateTime)
#
#    def __init__(self, name):
#        self.name = name
#        created = datetime.utcnow()

########################################################################################################################
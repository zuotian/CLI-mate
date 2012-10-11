"""
@organization: Leiden University Medical Center (LUMC)
@author: Zuotian Tatum
@contact: z.tatum@lumc.nl
"""

from climate import db
import surf

ns_dict = {
    'FOAF': 'http://xmlns.com/foaf/1.1/',
    'DCTerms': 'http://purl.org/dc/terms/',
    'CO': 'http://www.isi.edu/ikcap/Wingse/componentOntology.owl#',
    'FO': 'http://www.isi.edu/ikcap/Wingse/fileOntology.owl#',
    'CLP': 'http://cli-mate.lumc.nl/ontologies/clp#',
    'xsd': 'http://www.w3.org/2001/XMLSchema#',
    }

surf.ns.register(**ns_dict)

class Argument(db.EmbeddedDocument):
    name = db.StringField(required=True, max_length=50)
    arg_type = db.StringField(required=True, max_length=50,
                              choices=[(x, x) for x in ["None", "integer", "float", "string", "input", "output", "stdin", "stdout", "stderr"]])
    prefix = db.StringField(max_length=2)
    prefix_long = db.StringField(max_length=50)
    value = db.StringField(max_length=50)
    format = db.StringField(max_length=50)
    rank = db.IntField()

    choices = db.StringField(max_length=50)
    label = db.StringField(max_length=50)
    description = db.StringField(max_length=50)

    display = db.StringField(choices=[(x, x) for x in ["show", "hide", "show in advanced"]])
    min_occurrence = db.StringField(max_length=3)
    max_occurrence = db.StringField(max_length=50)

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

    arguments = db.ListField(db.EmbeddedDocumentField('Argument'))
    requirements = db.ListField(db.EmbeddedDocumentField('ToolRequirement'))

    def toRDF(self, format='turtle'):
        base_url = 'http://cli-mate.lumc.nl/data/definitions/clp#'
        store = surf.Store(reader='rdflib', writer='rdflib', rdflib_store='IOMemory')
        session = surf.Session(store)

        ComponentType = session.get_class(surf.ns.CLP['CommandLineProgramComponentType'])

        component_type = ComponentType(base_url + self.name)
        component_type.dcterms_label = self.name
        component_type.dcterms_title = self.binary
        component_type.dcterms_description = self.description
        component_type.co_hasVersion = self.version
        component_type.dcterms_comment = self.help
        component_type.save()

        session.commit()

        graph = session.default_store.reader.graph
        for prefix, url in ns_dict.items():
            graph.bind(prefix.lower(), url)

        return graph.serialize(format=format)




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
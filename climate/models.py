"""
@organization: Leiden University Medical Center (LUMC)
@author: Zuotian Tatum
@contact: z.tatum@lumc.nl
"""
from datetime import datetime
from climate import app, db
import surf

ns_dict = {
    'FOAF': 'http://xmlns.com/foaf/1.1/',
    'DCTerms': 'http://purl.org/dc/terms/',
    'CLP': 'http://cli-mate.lumc.nl/ontologies/clp#',
    'xsd': 'http://www.w3.org/2001/XMLSchema#'
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
        base_url = 'http://cli-mate.lumc.nl/data/definitions/default/%s#' % self.name
        store = surf.Store(reader='rdflib', writer='rdflib', rdflib_store='IOMemory')
        session = surf.Session(store)

        CommandLineProgram = session.get_class(surf.ns.CLP.CommandLineProgram)
        ExecutionRequirements = session.get_class(surf.ns.CLP.ExecutionRequirements)
        Software = session.get_class(surf.ns.CLP.Software)
        Argument = session.get_class(surf.ns.CLP.Argument)

        # set up main node.
        command_line_program = CommandLineProgram(base_url + self.name)
        command_line_program.dcterms_label = self.name
        command_line_program.dcterms_title = self.binary
        command_line_program.dcterms_description = self.description
        command_line_program.clp_hasVersion = self.version
        command_line_program.dcterms_comment = self.help
        command_line_program.save()

        # set up execution requirements
        execution_requirements = ExecutionRequirements(base_url + 'execution_requirements')
        command_line_program.clp_hasExecutionRequirements = execution_requirements
        execution_requirements.clp_requiresOperationSystem = surf.ns.CLP.Linux # TODO

        if self.interpreter != '(binary)':
            execution_requirements.clp_interpreter = surf.ns.CLP[self.interpreter]

        if self.grid_access_type != '-':
            execution_requirements.clp_gridAccessType = self.grid_access_type
            execution_requirements.clp_gridID = self.grid_access_location

        for req in self.requirements:
            software = Software(base_url + req.name)
            software.dcterms_tile = req.name
            software.clp_gridID = req.location
            software.clp_softwareType = req.type
            execution_requirements.clp_requiresSoftware = software
        execution_requirements.save()

        # add arguments
        argument_list = []
        for arg in self.arguments:
            argument = Argument(base_url + arg['name'])
            argument_list.append(argument)

            argument.clp_hasPrefix = arg['prefix']
            argument.clp_type = arg['arg_type']
            argument.save()
        command_line_program.clp_hasArgument = argument_list

        # add document metadata
        Agent = session.get_class(surf.ns.FOAF['Agent'])
        agent = Agent('http://climate.lumc.nl')
        agent.dcterms_title = app.config['TITLE']
        agent.dcterms_creator = app.config['AUTHOR']
        agent.dcterms_hasVersion = app.config['VERSION']
        agent.save()

        Document = session.get_class(surf.ns.DCTERMS['Document'])
        document = Document('')
        document.dcterms_creator = agent
        document.dcterms_created = datetime.utcnow()
        document.rdfs_label = 'RDF definition of %s' % self.name

        session.commit()

        # prepare for serialization
        graph = session.default_store.reader.graph
        for prefix, url in ns_dict.items():
            graph.bind(prefix.lower(), url)
        graph.bind('', base_url)

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
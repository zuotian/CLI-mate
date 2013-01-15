"""
@organization: Leiden University Medical Center (LUMC)
@author: Zuotian Tatum
@contact: z.tatum@lumc.nl
"""
from datetime import datetime
from flask.ext.security import RoleMixin, UserMixin, MongoEngineUserDatastore, Security
from climate import app, db
import surf

ns_dict = {
    'FOAF': 'http://xmlns.com/foaf/1.1/',
    'DCTerms': 'http://purl.org/dc/terms/',
    'CLP': 'http://cli-mate.lumc.nl/ontologies/clp#',
    'xsd': 'http://www.w3.org/2001/XMLSchema#'
}

surf.ns.register(**ns_dict)

class Role(db.Document, RoleMixin):
    name = db.StringField(required=True, unique=True, max_length=80)
    description = db.StringField(max_length=255)

class User(db.Document, UserMixin):
    email = db.StringField(unique=True, max_length=255)
    password = db.StringField(required=True, max_length=255)
    last_login_at = db.DateTimeField()
    current_login_at = db.DateTimeField()
    last_login_ip = db.StringField(max_length=100)
    current_login_ip = db.StringField(max_length=100)
    login_count = db.IntField()
    active = db.BooleanField(default=True)
    confirmed_at = db.DateTimeField()
    roles = db.ListField(db.ReferenceField(Role), default=[])

# Setup Flask-Security
user_datastore = MongoEngineUserDatastore(db, User, Role)
security = Security(app, user_datastore)

class Dependency(db.EmbeddedDocument):
    source = db.StringField(max_length=50, required=True)
    source_condition = db.StringField(max_length=50, required=True, choices=[(x, x) for x in ["display", "format", "value"]])
    target_scope = db.StringField(max_length=50, required=True)
    target_effect = db.StringField(max_length=150)

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

    dependencies = db.ListField(db.EmbeddedDocumentField(Dependency))

    def toRDF(self, node):
        """
        serialize an argument in RDF triples.
        """
        node.dcterms_title = self.name
        if self.arg_type != "None":
            node.clp_type = surf.ns.CLP[self.arg_type]
        node.clp_hasPrefix = self.prefix
        node.clp_hasLongPrefix = self.prefix_long
        node.clp_value = self.value
        node.clp_format = self.format
        node.rank = self.rank
        node.dcterms_label = self.label
        node.dcterms_description = self.description
        node.save()

    def fromRDF(self, node):
        pass

class ToolRequirement(db.EmbeddedDocument):
    type = db.StringField(choices=[(x, x) for x in ["binary", "python-module"]])
    name = db.StringField(max_length=50),
    location = db.StringField(max_length=200)

class Tool(db.Document):
    # meta data
    submitter = db.ReferenceField(User)
    last_modified = db.DateTimeField()
    is_public = db.BooleanField(default=False)

    name = db.StringField(required=True, max_length=50)
    binary = db.StringField(required=True, max_length=50)
    description = db.StringField(max_length=100)
    author = db.StringField(max_length=50)
    email = db.EmailField()
    version = db.StringField(max_length=50)
    help = db.StringField()

    os = db.StringField(choices=[(x, x) for x in ["Linux"]])
    interpreter = db.StringField(choices=[(x, x) for x in ["(binary)", "bash", "python", "perl", "java"]])
    grid_access_type = db.StringField(choices=[(x, x) for x in ["-", "LFN", "URL"]])
    grid_access_location = db.StringField(max_length=250)

    arguments = db.ListField(db.EmbeddedDocumentField(Argument))
    requirements = db.ListField(db.EmbeddedDocumentField(ToolRequirement))

    def toRDF(self, format='turtle'):
        base_url = 'http://cli-mate.lumc.nl/data/definitions/default/%s#' % self.name
        store = surf.Store(reader='rdflib', writer='rdflib', rdflib_store='IOMemory')
        session = surf.Session(store)

        # set up RDF classes.
        CLPCommandLineProgram = session.get_class(surf.ns.CLP.CommandLineProgram)
        CLPExecutionRequirements = session.get_class(surf.ns.CLP.ExecutionRequirements)
        CLPSoftware = session.get_class(surf.ns.CLP.Software)
        CLPArgument = session.get_class(surf.ns.CLP.Argument)

        # set up main node.
        command_line_program = CLPCommandLineProgram(base_url + self.name)
        command_line_program.dcterms_label = self.name
        command_line_program.dcterms_title = self.binary
        command_line_program.dcterms_description = self.description
        command_line_program.clp_hasVersion = self.version
        command_line_program.dcterms_comment = self.help
        command_line_program.save()

        # set up execution requirements
        execution_requirements = CLPExecutionRequirements(base_url + 'execution_requirements')
        command_line_program.clp_hasExecutionRequirements = execution_requirements
        execution_requirements.clp_requiresOperationSystem = surf.ns.CLP.Linux # TODO

        if self.interpreter != '(binary)':
            execution_requirements.clp_interpreter = surf.ns.CLP[self.interpreter]

        if self.grid_access_type != '-':
            execution_requirements.clp_gridAccessType = self.grid_access_type
            execution_requirements.clp_gridID = self.grid_access_location

        for req in self.requirements:
            software = CLPSoftware(base_url + req.name)
            software.dcterms_tile = req.name
            software.clp_gridID = req.location
            software.clp_softwareType = req.type
            execution_requirements.clp_requiresSoftware = software
        execution_requirements.save()

        # add arguments
        argument_list = []
        for arg in self.arguments:
            argument = Argument(**arg)
            argument_node = CLPArgument(base_url + arg['name'])
            argument.toRDF(argument_node)
            argument_list.append(argument_node)
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


class Template(db.Document):
    name = db.StringField(max_length=128, required=True)
    platform = db.ListField(db.StringField())
    path = db.StringField()
    author = db.ReferenceField(User)
    last_modified = db.DateTimeField()

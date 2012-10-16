"""
@organization: Leiden University Medical Center (LUMC)
@author: Zuotian Tatum
@contact: z.tatum@lumc.nl
"""


#!/usr/bin/python
"""
Use a tool definition and a template to compile an interface.

@organization: Leiden University Medical Center (LUMC)
@author: Zuotian Tatum
@contact: z.tatum@lumc.nl
@license: GPLv2 or later

@requires: rdflib (version > 3.0)
"""

import json
from datetime import datetime

from rdflib import Graph, Namespace, Literal, BNode, URIRef
from rdflib import RDF, RDFS
from rdflib.collection import Collection

import climate

#RDF namespaces.
DCTerms = Namespace('http://purl.org/dc/terms/')
FOAF = Namespace('http://xmlns.com/foaf/1.1/')
Component = Namespace('http://www.isi.edu/ikcap/Wingse/componentOntology.owl#')
FO = Namespace('http://www.isi.edu/ikcap/Wingse/fileOntology.owl#')
CLP = Namespace('http://www.humgen.nl/climate/ontologies/clp#')

# for back compact
CLI = Namespace('http://www.ontology.liacs.nl/cli#')
Process = Namespace('http://www.daml.org/services/owl-s/1.1/Process.owl#')


def _e(string):
    return string.replace(' ', '_')

class DefinitionDesigner():
    """
    Handle tasks related to creating a command line program definition.
        - generate RDF xml from a data structure.
        - parse RDF xml into a data structure.

    TODO: update this data structure.
    The data structure is defined as following
        {
            name : "name of the tool",
            binary : "name of binary",
            description : "short description of the tool",
            help : "long description of the tool",
            version: "current version number",
            owner: "name of the tool creator",
            email: "email of the tool creator",
            parameter : [{
                name : "name of the parameter",
                type : "parameter type, possible values are:
                        None, boolean, integer, string, select, input, output,
                        stdin, stdout, stderr",
                arg : "parameter short notation, such as -a for all",
                value : "parameter value",
                label : "short description of the parameter",
                description : "long description of the parameter",
                rank : "partial ordering of the parameter",
                display : "always-show/always-hide/show-in-advanced",
                repeatable: "True/False",
                depends : "name of the depending parameter",
                depending_condition : "value of the depending parameter when
                                       the dependency takes place"
                property_bag : "JSON formatted string that contains properties
                                specific for target template generation."
            }]
        }
    """
    def __init__(self):
        self.graph = Graph()
        self.configGraph = None
        self.j_encoder = json.JSONEncoder()
    #def __init__

    def _generateStatements(self, subject_node, properties):
        """
        properties = {"from_loc" : ["data_table", "no"]
                      "access_location : ["/path/to/somewhere/", "yes"]}
        """
        for (key, values) in properties.items():
            if values[1] == 'no': # not a volatile property.
                a_node = BNode()
                self._addTriple(a_node, RDF['type'], RDF['Statement'])
                self._addTriple(a_node, CLP['relatedTo'], Literal(key))
                self._addTriple(a_node, RDF['subject'], subject_node)
                self._addTriple(a_node, RDF['predicate'], CLP['hasProperty'])
                self._addTriple(a_node, RDF['object'], values[0])
    #def generateStatements

    def _generateDependencies(self, ap_node, dependencies):
        if dependencies:
            for dep in dependencies:
                d_node = BNode()
                self._addTriple(d_node, RDF.type, CLP['dependency'])
                self._addTriple(d_node, CLP['hasDependingItem'], BNode(_e(dep['depending_parameter'])))
                self._addTriple(d_node, CLP['dependingCondition'], dep['depending_condition'])
                self._addTriple(d_node, CLP['hasDependentItem'], ap_node)
                self._addTriple(d_node, CLP['dependentScope'], dep['dependent_scope'])
                self._addTriple(d_node, CLP['effect'], dep['dependent_effect'])

    def _addTriple(self, s, p, o):
        if type(o) in [BNode, URIRef]:
            self.graph.add((s, p, o))
        elif type(o) is list:
            o_list = BNode()
            self.graph.add((s, p, o_list))
            os = Collection(self.graph, o_list)
            for item in o:
                os.append(Literal(item))
        elif o != '':
            self.graph.add((s, p, Literal(o)))

    #def _addTriple

    def _dictToGraph(self, data):
        t_node = BNode(_e(data['name']))
        self._addTriple(t_node, RDF.type, CLP['CommandLineProgramComponentType'])
        self._addTriple(t_node, DCTerms['label'], data['name'])
        self._addTriple(t_node, DCTerms['title'], data['binary'])
        self._addTriple(t_node, DCTerms['description'], data['description'])
        self._addTriple(t_node, Component['hasVersion'], data['version'])
        self._addTriple(t_node, DCTerms['comment'], data['help'])
        self._generateStatements(t_node, data['property_bag'])

        r_node = BNode()
        self._addTriple(t_node, Component['hasExecutionRequirements'], r_node)
        self._addTriple(r_node, RDF.type, Component['ExecutionRequirements'])
        self._addTriple(r_node, Component['requiresOperationSystem'], Component['Linux']) # TODO
        if data['interpreter'] != '(binary)':
            self._addTriple(r_node, Component['requiresSoftware'], Component[data['interpreter']])
        if data['grid_access_type'] != '-':
            self._addTriple(r_node, CLP['gridAccessType'], data['grid_access_type'])
            self._addTriple(r_node, Component['gridID'], data['grid_access_location'])
        for req in data['requirements']:
            req_node = BNode()
            self._addTriple(r_node, CLP['requiresSoftware'], req_node)
            self._addTriple(req_node, RDF.type, CLP['Software'])
            self._addTriple(req_node, DCTerms['title'], req['req_name'])
            self._addTriple(req_node, CLP['gridID'], req['req_location'])
            self._addTriple(req_node, CLP['softwareType'], req['req_type'])

        argument_list = BNode('argument_list')
        self._addTriple(t_node, Component['hasArguments'], argument_list)
        #self._addTriple(argument_list, RDF.type, Component['argumentAndPrefixList'])
        argument_nodes = Collection(self.graph, argument_list)

        input_list = BNode('input_list')
        self._addTriple(t_node, Component['hasInputs'], input_list)
        #self._addTriple(input_list, RDF.type, Component['FileOrCollectionList'])
        input_nodes = Collection(self.graph, input_list)

        output_list = BNode('output_list')
        self._addTriple(t_node, Component['hasOutputs'], output_list)
        #self._addTriple(output_list, RDF.type, Component['FileOrCollectionList'])
        output_nodes = Collection(self.graph, output_list)

        for p in data['parameters']:
            ap_node = BNode(_e(p['name']))
            argument_nodes.append(ap_node)
            self._addTriple(ap_node, RDF.type, Component['ArgumentAndPrefix'])

            a_node = BNode(_e(p['name']) + '_arg')
            self._addTriple(ap_node, Component['hasArgument'], a_node)

            choices = []
            if p['choices']:
                choices = map(lambda x: x.strip(), p['choices'].split(','))

            p_type = p['type']
            if p_type == 'integer':
                self._addTriple(a_node, RDF.type, FO['Int'])
                try:
                    self._addTriple(a_node, FO['hasIntValue'], int(p['value']))
                    choices = map(lambda x: int(x), choices)
                except ValueError:
                    pass # do nothing if value is not an integer
            elif p_type == 'float':
                self._addTriple(a_node, RDF.type, FO['Float'])
                try:
                    self._addTriple(a_node, FO['hasFloatValue'], float(p['value']))
                    choices = map(lambda x: float(x), choices)
                except ValueError:
                    pass # do nothing if value is not a float
            elif p_type in ['string', 'select']:
                self._addTriple(a_node, RDF.type, FO['String'])
                self._addTriple(a_node, FO['hasStringValue'], p['value'])
            elif p_type in ['input', 'stdin']:
                self._addTriple(a_node, RDF.type, FO['File'])
                self._addTriple(a_node, DCTerms['format'], p['format'])
                self._addTriple(a_node, Component['hasValue'], p['value'])
                input_nodes.append(a_node)
            elif p_type in ['output', 'stdout', 'stderr']:
                self._addTriple(a_node, RDF.type, FO['File'])
                self._addTriple(a_node, DCTerms['format'], p['format'])
                self._addTriple(a_node, Component['hasValue'], p['value'])
                output_nodes.append(a_node)
            else:
                self._addTriple(a_node, Component['hasValue'], p['value'])

            if choices:
                choices = map(lambda x: Literal(x), choices)
                choice_list = BNode(_e(p['name'] + '_choice_list'))
                choice_nodes = Collection(self.graph, choice_list, choices)
                self._addTriple(a_node, CLP['hasValueChoices'], choice_list)

            self._addTriple(ap_node, DCTerms['title'], p['name'])
            self._addTriple(ap_node, DCTerms['description'], p['description'])
            self._addTriple(ap_node, RDFS.label, p['label'])
            self._addTriple(ap_node, Component['hasPrefix'], p['arg'])
            self._addTriple(ap_node, CLP['hasAlternativePrefix'], p['arg_long'])
            self._addTriple(ap_node, CLP['order'], int(p['rank']))
            self._addTriple(ap_node, CLP['display'], p['display'])
            self._addTriple(ap_node, CLP['minOccurrence'], p['min_occurrence'])
            self._addTriple(ap_node, CLP['maxOccurrence'], p['max_occurrence'])

            self._generateStatements(ap_node, p['property_bag'])
            self._generateDependencies(ap_node, p['dependencies'])
        #for
    #def _dictToGraph

    def _addMetaInfo(self, data):
        # meta data node about the Interface Generator itself.
        ig_node = URIRef(climate.host_url)
        self._addTriple(ig_node, RDF.type, FOAF['Agent'])
        self._addTriple(ig_node, DCTerms['title'], climate.__title__)
        self._addTriple(ig_node, DCTerms['creator'], climate.__author__)
        self._addTriple(ig_node, DCTerms['hasVersion'], climate.__version__)

        m_node = URIRef('')
        self._addTriple(m_node, RDF.type, FOAF['Document'])
        self._addTriple(m_node, DCTerms['creator'], ig_node)
        self._addTriple(m_node, DCTerms['created'], datetime.utcnow())
        self._addTriple(m_node, RDFS['label'], 'RDF Definition of ' + data['name'])
    #_addMetaInfo

    def generateDefinition(self, data, format='n3'):
        #TODO: current RDFLib doesn't support base url serialization!
        base_uri = climate.tool_repository_url + _e(data['name']) + '.rdf#'
        Base = Namespace(base_uri)
        self.graph.bind('base', Base)

        self.graph.bind('dcterms', DCTerms)
        self.graph.bind('foaf', FOAF)
        self.graph.bind('co', Component)
        self.graph.bind('fo', FO)
        self.graph.bind('clp', CLP)

        self._dictToGraph(data)
        self._addMetaInfo(data)
        return self.graph.serialize(format=format)
    #def generateDefinition

    def _parseObjectStr(self, s, p):
        o = self.graph.value(s, p)
        if type(o) == Literal:
            return o.decode()
        elif type(o) == BNode:
            title = self.graph.value(o, DCTerms['title'])
            return title.decode()
        else:
            return ''
    #def _parseObjectStr

    def _parseStatements(self, o):
        bag = {}
        for s_node in self.graph.subjects(predicate=RDF.subject, object=o):
            # make sure it is a statement
            if self.graph.value(subject=s_node, predicate=RDF.type) == RDF.Statement:
                bag[self._parseObjectStr(s_node, CLP['relatedTo'])] = [self._parseObjectStr(s_node, RDF.object), 'no']

        return bag
    #def _parseStatements

    def _parseDependencies(self, node):
        dependencies = []
        for d in self.graph.subjects(CLP['hasDependentItem'], node):
            dependencies.append({
                'depending_parameter' : self._parseObjectStr(d, CLP['hasDependingItem']),
                'depending_condition' : self._parseObjectStr(d, CLP['dependingCondition']),
                'dependent_scope' : self._parseObjectStr(d, CLP['dependentScope']),
                'dependent_effect' : self._parseObjectStr(d, CLP['effect'])
            })
        return dependencies
    #def _parseDependencies

    def _parseFile(self, handle):
        if type(handle) is file:
            content = handle.read()
        else:
            content = handle

        if content[0] == '@':       #turtle
            self.graph.parse(data=content, format='n3')
        elif content[0] == '<':     #xml
            self.graph.parse(data=content)
    #def _parseFile

    def _parseType(self, node_type):
        return self.graph.subjects(predicate=RDF.type, object=node_type)
    #def _parseType

    def parseDefinition(self, handle):
        """
        Parse a RDF file.
        The base ontology is ComponentOntology.

        """
        self._parseFile(handle)

        version = self._parseObjectStr(
            self.graph.value(predicate=RDF.type, object=FOAF['Agent']),
            DCTerms['hasVersion'])

        if version in ['0.1', '0.2']:
            data = self.parseDefinitionBackCompat(self.graph, version)
            data['interpreter'] = '(binary)'
            for p in data['parameters']:
                # newly added properties
                p['min_occurrence'] = '1' if p['required'] else ''
                p['max_occurrence'] = '' if p['repeatable'] else '1'

                # choices property is added, populate with values from from value property.
                if ',' in p['value']:
                    p['choices'] = p['value']
                    p['value'] = p['value'].split(',')[0].strip()
                else:
                    p['choices'] = ''

                # type convertions
                if p['type'] == 'stdin':
                    p['arg'] = p['arg'] or '<'
                elif p['type'] == 'stdout':
                    p['arg'] = p['arg'] or '>'
                elif p['type'] == 'stderr':
                    p['arg'] = p['arg'] or '2>'
                elif p['type'] == 'select':
                    p['type'] = 'string'
                elif p['type'] == 'boolean':
                    p['type'] == 'None'

                # move argument with long form into arg_long
                if p['arg'].startswith('--'):
                    p['arg_long'] = p['arg']
                    p['arg'] = ''

                # add volatile flag for property bag
                if p['property_bag']:
                    for (key, value) in p['property_bag'].items():
                        p['property_bag'][key] = [value, 'no']

            return data


        data = {'message': ''}

        t_node = self._parseType(CLP['CommandLineProgramComponentType'])

        try:
            t_node = t_node.next()
        except StopIteration:
            data['message'] = 'CommandLineProgramComponentType is missing.'
            return data

        data['name'] = self._parseObjectStr(t_node, DCTerms['label'])
        data['binary'] = self._parseObjectStr(t_node, DCTerms['title'])
        data['description'] = self._parseObjectStr(t_node, DCTerms['description'])
        data['version'] = self._parseObjectStr(t_node, DCTerms['hasVersion'])
        data['help'] = self._parseObjectStr(t_node, DCTerms['comment']).replace("\r\n", "\n")
        data['property_bag'] = self._parseStatements(t_node)

        r_node = self._parseType(Component['ExecutionRequirements']).next()
        data['os'] = 'Linux' #TODO
        data['interpreter'] = self._parseObjectStr(r_node, Component['requiresSoftware']) or '(binary)'
        data['grid_access_type'] = self._parseObjectStr(r_node, CLP['gridAccessType'])
        data['grid_access_location'] = self._parseObjectStr(r_node, Component['gridID'])
        data['requirements'] = []

        data['meta'] = {}
        m_node = self._parseType(FOAF['Document']).next()
        data['meta']['label'] = self._parseObjectStr(m_node, RDFS['label'])
        data['meta']['time'] = self._parseObjectStr(m_node, DCTerms['created'])
        data['meta']['version'] = version

        s_nodes = self._parseType(CLP['Software'])
        if s_nodes:
            for s_node in s_nodes:
                data['requirements'].append({
                    'req_name' : self._parseObjectStr(s_node, DCTerms['title']),
                    'req_location' : self._parseObjectStr(s_node, CLP['gridID']),
                    'req_type' : self._parseObjectStr(s_node, CLP['softwareType'])
                })

        input_list = Collection(self.graph, self.graph.value(t_node, Component['hasInputs']))
        output_list = Collection(self.graph, self.graph.value(t_node, Component['hasOutputs']))
        argument_list = Collection(self.graph, self.graph.value(t_node, Component['hasArguments']))

        data['parameters'] = []
        for p_node in argument_list:
            parameter = {
                'name' : self._parseObjectStr(p_node, DCTerms['title']),
                'description' : self._parseObjectStr(p_node, DCTerms['description']),
                'label' : self._parseObjectStr(p_node, RDFS.label),
                'arg' : self._parseObjectStr(p_node, Component['hasPrefix']),
                'arg_long' : self._parseObjectStr(p_node, CLP['hasAlternativePrefix']),
                'rank' : self._parseObjectStr(p_node, CLP['order']),
                'display' : self._parseObjectStr(p_node, CLP['display']),
                'min_occurrence' : self._parseObjectStr(p_node, CLP['minOccurrence']),
                'max_occurrence' : self._parseObjectStr(p_node, CLP['maxOccurrence']),
                'property_bag' : self._parseStatements(p_node),
                'dependencies' : self._parseDependencies(p_node),
                'choices' : '',
                'value' : ''
            }

            arg_node = self.graph.value(p_node, Component['hasArgument'])
            if arg_node:
                arg_type = self.graph.value(arg_node, RDF.type)
                choices = Collection(self.graph, self.graph.value(arg_node, CLP['hasValueChoices']))

                if choices:
                    parameter['choices'] = ', '.join(choices)

                if arg_type == FO['Int']:
                    parameter['type'] = 'integer'
                    parameter['value'] = self._parseObjectStr(arg_node, FO['hasIntValue'])
                elif arg_type == FO['Float']:
                    parameter['type'] = 'float'
                    parameter['value'] = self._parseObjectStr(arg_node, FO['hasFloatValue'])
                elif arg_type == FO['String']:
                    parameter['type'] = 'string'
                    parameter['value'] = self._parseObjectStr(arg_node, FO['hasStringValue'])
                elif arg_type == FO['File']:
                    parameter['format'] = self._parseObjectStr(arg_node, DCTerms['format'])
                    parameter['value'] = self._parseObjectStr(arg_node, Component['hasValue'])
                    if arg_node in input_list:
                        if parameter['arg'] == '<':
                            parameter['type'] = 'stdin'
                        else:
                            parameter['type'] = 'input'
                    elif arg_node in output_list:
                        if parameter['arg'] == '>':
                            parameter['type'] = 'stdout'
                        elif parameter['arg'] == '2>':
                            parameter['type'] = 'stderr'
                        else:
                            parameter['type'] = 'output'
                else:
                    parameter['type'] = 'None'
                    parameter['value'] = self._parseObjectStr(arg_node, Component['hasValue'])

            #end if

            data['parameters'].append(parameter)
            #end for

        # no need to sort parameters because the order is preserved in the collection structure.
        # sort parameter base on its partial order / rank
        # data['parameters'].sort(key=lambda n: n['rank'])

        return data

    def parseDefinitionBackCompat(self, graph, rdf_version, deepParse=True):
        """
        Parse a RDF file with version 0.1 and 0.2.

        Version 0.1 uses OWL-S Process as the base ontology.
        Version 0.2 describes property bags with RDF Statements.

        @arg graph:
            RDF graph containing the tool definition.
        @arg deepParse:
            If true, the value of a select parameter will be returned
            as a list. Otherwise, returned as a string. default is true.

        @return: Tool definition in a dictionary.
                 Parameters are sorted by rank.
                 See RDFHepler for the dictionary structure.
        @rtypes: dictionary

        """

        data = {'message': 'The definition format has been upgraded to a \
            newer format. Please save your definition in the new format.'}

        # for property bag.
        j_encoder = json.JSONEncoder()
        j_decoder = json.JSONDecoder()

        def getObjectStr(s, p):
            o = graph.value(s, p)
            if type(o) == Literal:
                return o.decode()
            elif type(o) == BNode:
                title = graph.value(o, DCTerms['title'])
                return title.decode()
            else:
                return ''
        #getObjectStr

        def getPropertyBag(node):
            if rdf_version == '0.1':
                # keep this for back compat
                bag_string = getObjectStr(node, CLI['propertyBag'])
                if deepParse:
                    # convert value of a select parameter into a list.
                    try:
                        return j_decoder.decode(bag_string)
                    except:
                        return None

                return bag_string

            else:
                bag = {}
                for prop in graph.subjects(predicate=RDF.subject, object=node):
                    # make sure it is a statement
                    if graph.value(subject=prop, predicate=RDF.type) == RDF.Statement:
                        bag[getObjectStr(prop, CLI['relatedTo'])] = [getObjectStr(prop, RDF.object), 'no']

                if not deepParse:
                    return '' if not bag else j_encoder.encode(bag)

                return bag
        #getPropertyBag

        def getDependencies(node):
            dependencies = []
            for d in graph.subjects(CLI['dependent_parameter'], node):
                dependencies.append({
                    'depending_parameter' : getObjectStr(d, CLI['depending_parameter']),
                    'depending_condition' : getObjectStr(d, CLI['depending_condition']),
                    'dependent_scope' : getObjectStr(d, CLI['dependent_scope']),
                    'dependent_effect' : getObjectStr(d, CLI['dependent_effect'])
                })
            return dependencies
        #getDependencies


        i_node = graph.value(predicate=RDF.type, object=Process['Process'])
        data['name'] = getObjectStr(i_node, DCTerms['title'])
        data['binary'] = getObjectStr(i_node, Process['name'])
        data['description'] = getObjectStr(i_node, DCTerms['description'])
        data['version'] = getObjectStr(i_node, DCTerms['hasVersion'])
        data['help'] = getObjectStr(i_node, DCTerms['instructionalMethod']).replace("\r\n", "\n")
        data['property_bag'] = getPropertyBag(i_node)

        c_node = graph.value(predicate=RDF.type, object=FOAF['person'])
        data['owner'] = getObjectStr(c_node, FOAF['name'])
        data['email'] = getObjectStr(c_node, FOAF['mbox'])

        data['meta'] = {}
        m_node = graph.value(predicate=RDF.type, object=FOAF['Document'])
        data['meta']['label'] = getObjectStr(m_node, RDFS['label'])
        data['meta']['time'] = getObjectStr(m_node, DCTerms['created'])
        data['meta']['version'] = rdf_version

        data['parameters'] = []
        for p in graph.objects(i_node, Process['hasParameter']):
            data['parameters'].append({
                "type" : getObjectStr(p, Process['parameterType']),
                'name' : getObjectStr(p, DCTerms['title']),
                'arg' : getObjectStr(p, CLI['argument']),
                'arg_long' : getObjectStr(p, CLI['argument_alternative']),
                'value' : getObjectStr(p, Process['parameterValue']),
                'label' : getObjectStr(p, RDFS.label),
                'description' : getObjectStr(p, DCTerms['description']),
                'rank' : getObjectStr(p, CLI['order']),
                'format' : getObjectStr(p, DCTerms['format']),
                'display' : getObjectStr(p, CLI['display']),
                'repeatable' : getObjectStr(p, CLI['repeatable']),
                'required' : getObjectStr(p, CLI['required']),
                'property_bag' : getPropertyBag(p),
                'dependencies' : getDependencies(p)
            })
            #endfor

        # sort parameter base on its partial order / rank
        data['parameters'].sort(key=lambda n: n['rank'])

        return data
    #parseRDF
#DefinitionDesigner
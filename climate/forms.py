"""
@organization: Leiden University Medical Center (LUMC)
@author: Zuotian Tatum
@contact: z.tatum@lumc.nl
"""

from flask.ext.mongoengine.wtf import model_form
from flask.ext.wtf import (Form, FileField, SubmitField, FieldList, FormField)
from climate.models import (Tool, Parameter, ToolRequirement)

ParameterFormBase = model_form(Parameter, field_args={
    'name': {'label' : 'Name *'},
    'arg': {'label': "Argument (short)"},
    'arg_long': {'label': "Argument (long)"},
    'value': {'label': "Default value"},
    'choices': {'label': "Restrict argument values (use \",\" to separate values)"},
    'label': {'label': "Label (short description)"},
    'description': {'label': "Help (hint)"},
    'min_occurrence': {'description': "0"},
    'max_occurrence': {'description': "1 (use ? for unlimited)"}
})

class ParameterForm(ParameterFormBase):
    field_set = {
        'left' : ('type', 'name', 'arg', 'arg_long', 'value', 'format', 'rank'),
        'right': ('choices', 'label', 'description'),
        'advanced': ('display', 'min_occurrence', 'max_occurrence')
    }

ToolRequirementForm = model_form(ToolRequirement, field_args={
    'type': {'label': "Requirement type"},
    'name': {'label': "Requirement name"},
    'location': {'label': "LFN location"}
})

ToolFormBase = model_form(Tool, exclude=('parameters', 'requirements'), field_args={
    'name': {'label': "Name *"},
    'binary': {'label': "Command *"},
    'email': {'label': "Owner Email"},
    'help': {'label': "Enter the help manual below."},
    'grid_access_type': {'label': "GRID access"}
})

class ToolForm(ToolFormBase):

    requirements = FieldList(FormField(ToolRequirementForm))
    parameters = FieldList(FormField(ParameterForm))

    field_set = {
        'general': ('name', 'binary', 'description', 'owner', 'email', 'version', 'help'),
        'runtime': ('os', 'interpreter', 'grid_access_type', 'grid_access_location')
    }

class ToolUploadForm(Form):
    rdf = FileField(description="Load a RDF definition")
    submit = SubmitField("Upload")

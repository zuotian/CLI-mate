"""
@organization: Leiden University Medical Center (LUMC)
@author: Zuotian Tatum
@contact: z.tatum@lumc.nl
"""

from flask.ext.wtf import (Form, TextField, TextAreaField, FileField,
                           SubmitField, SelectField, HiddenField)

class ToolUploadForm(Form):
    rdf = FileField(description="Load a RDF definition")
    submit = SubmitField("Upload")

class ToolForm(Form):
    name = TextField("Name *")
    binary = TextField("Command *")
    description = TextField("Description")
    owner = TextField("Owner")
    email = TextField("Owner Email")
    version = TextField("Version")
    help = TextAreaField("Enter the help manual below.")


class ParameterForm(Form):
    TYPE_CHOICES = ["None", "integer", "float", "string",
                    "input", "output", "stdin", "stdout", "stderr"]
    DISPLAY_CHOICES = ["show", "hide", "show in advanced"]
    parameter_type = SelectField("Type", choices=[(x, x) for x in TYPE_CHOICES])
    name = TextField("Name *")
    arg = TextField("Argument (short)")
    arg_long = TextField("Argument (long)")
    value = TextField("Default Value")
    format = TextField("Format")
    rank = HiddenField("rank")

    choices = TextField("Restrict argument values (use \",\" to separate values)")
    label = TextField('Label (short description)')
    description = TextField("Help (hint)")

    display = SelectField("Display", choices=[(x, x) for x in DISPLAY_CHOICES])
    min_occurrence = TextField("Min Occurrence", description="0"),
    max_occurrence = TextField("Max Occurrence", description="1 (use ? for unlimited)")

    field_set = {
        'left' : ('parameter_type', 'name', 'arg', 'arg_long', 'value', 'format', 'rank'),
        'right': ('choices', 'label', 'description'),
        'advanced': ('display', 'min_occurrence', 'max_occurrence')
    }

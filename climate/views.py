"""
@organization: Leiden University Medical Center (LUMC)
@author: Zuotian Tatum
@contact: z.tatum@lumc.nl
"""
from jinja2 import Template
import os
from flask import render_template, url_for, redirect, make_response, request
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers import guess_lexer_for_filename
from pygments.lexers.agile import PythonLexer
from pygments.util import ClassNotFound

from climate import app
from climate.forms import ToolForm, ToolUploadForm, ArgumentForm
from climate.models import Tool, Argument
from climate.utils.sw_lexer import Notation3Lexer


@app.context_processor
def view_context():
    return {
        'menu': [['About Us', 'about'],
                 ['Interface Generation', 'generate'],
                 ['Tool Definition', 'define']]}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/define/upload', methods=['GET', 'POST'])
def define_upload():
    upload_form = ToolUploadForm()
    if upload_form.validate_on_submit():
        from climate.utils.legacy_parser import DefinitionDesigner

        d = DefinitionDesigner()
        data = d.parseDefinition(upload_form.rdf.data.read())
        tool = Tool(name=data['name'], arguments=[Argument(**p) for p in data['parameters']])
        form = ToolForm(csrf_enabled=True, obj=tool, formdata=None)
        return render_template('tool/define.html', form=form, empty_argument_form=ArgumentForm())
    else:
        return render_template('tool/upload.html', form=upload_form)


@app.route('/define')
def define():
    return redirect(url_for('define_new'))


@app.route('/define/new')
def define_new():
    # add a placeholder argument, so that arguments tab is not empty.
    tool = Tool(name='test', arguments=[Argument(name='Argument1')])
    form = ToolForm(csrf_enabled=True, obj=tool)
    return render_template('tool/define.html', form=form, empty_argument_form=ArgumentForm())


@app.route('/define/<string:action>', methods=['POST'])
def define_ajax(action):
    form = ToolForm()
    tool = Tool(**form.data)
    if action == 'show':
        return highlight(tool.toRDF(rdf_format='turtle'), Notation3Lexer(), HtmlFormatter())
    elif action == 'download':
        return make_response(tool.toRDF(rdf_format='turtle'), 200,
                             [('Content-Type', 'rdf/ttl'),
                              ('Content-disposition', 'attachment; filename=%s.ttl' % tool.name)])
    elif action == 'generate':
        target_file = open(os.path.join(app.config['TEMPLATE_DIR'], request.form['template_name']), 'r')
        target = Template(target_file.read())
        code = tool.toTarget(target)
        try:
            lexer = guess_lexer_for_filename(request.form['template_name'], code)
        except ClassNotFound:
            lexer = PythonLexer()  # default
        return highlight(code, lexer, HtmlFormatter())
    else:
        return make_response("Unknown action '%s'" % action, 401)


@app.route('/generate')
def generate():
    pass


@app.route('/about')
def about():
    return render_template('about.html')
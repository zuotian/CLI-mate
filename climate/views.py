"""
@organization: Leiden University Medical Center (LUMC)
@author: Zuotian Tatum
@contact: z.tatum@lumc.nl
"""
from flask import render_template
from flask.ext.mongoengine.wtf import model_form
from pygments import highlight
from pygments.formatters.html import HtmlFormatter

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

@app.route('/define/upload')
def define_upload():
    upload_form = ToolUploadForm()
    return render_template('tool/upload.html', upload_form=upload_form)

@app.route('/define')
def define():
    form = model_form(Argument)
    return render_template('define.html',  form=form, data={})

@app.route('/define/new')
def define_new():
    # add a placeholder argument, so that arguments tab is not empty.
    tool = Tool(name='test', arguments=[Argument(name='Argument1')])
    form = ToolForm(csrf_enabled=True, obj=tool)
    return render_template('tool/define.html', form=form, empty_argument_form=ArgumentForm())

@app.route('/define/show_rdf', methods=['POST'])
def show_rdf():
    form = ToolForm()
    tool = Tool(**form.data)
    rdf = tool.toRDF(format='turtle')
    return highlight(rdf, Notation3Lexer(), HtmlFormatter())

@app.route('/generate')
def generate():
    pass

@app.route('/about')
def about():
    return render_template('about.html')
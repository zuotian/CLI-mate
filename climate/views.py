"""
@organization: Leiden University Medical Center (LUMC)
@author: Zuotian Tatum
@contact: z.tatum@lumc.nl
"""
from flask import render_template
from flask.ext.mongoengine.wtf import model_form

from climate import app
from .forms import ToolForm, ToolUploadForm
from .models import Tool, Parameter

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
    form = model_form(Parameter)
    return render_template('define.html',  form=form, data={})

@app.route('/define/new')
def define_new():
    tool = Tool(name='test')
    tool.parameters.append(Parameter(name='parameter1'))
    form = ToolForm(csrf_enabled=True, obj=tool)
    return render_template('tool/new.html', form=form, data={})

@app.route('/generate')
def generate():
    pass

@app.route('/about')
def about():
    return render_template('about.html')
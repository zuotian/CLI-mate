"""
@organization: Leiden University Medical Center (LUMC)
@author: Zuotian Tatum
@contact: z.tatum@lumc.nl
"""
from flask import render_template

from climate import app
from .forms import ToolForm, ToolUploadForm, ParameterForm

view_context = {
    'menu' : [
        ['About Us', 'about'],
        ['Interface Generation', 'generate'],
        ['Tool Definition', 'define']],
    'version' : app.config['VERSION'],
    'debug_js' : app.config['DEBUG']
}

@app.route('/')
def index():
    return render_template('index.html', **view_context)

@app.route('/define/upload')
def define_upload():
    upload_form = ToolUploadForm()
    return render_template('tool/upload.html', upload_form=upload_form, **view_context)

@app.route('/define')
def define():
    form = ToolForm(csrf_enabled=True)
    return render_template('define.html',  form=form, data={}, **view_context)

@app.route('/define/new')
def define_new():
    form = ToolForm(csrf_enabled=True)
    parameter_form = ParameterForm()
    return render_template('tool/new.html', form=form, parameter_form=parameter_form, data={}, **view_context)

@app.route('/generate')
def generate():
    pass

@app.route('/about')
def about():
    return render_template('about.html', **view_context)
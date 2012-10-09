"""
@organization: Leiden University Medical Center (LUMC)
@author: Zuotian Tatum
@contact: z.tatum@lumc.nl
"""
from flask import render_template

from climate import app

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

@app.route('/define')
def define():
    pass

@app.route('/generate')
def generate():
    pass

@app.route('/about')
def about():
    return render_template('about.html', **view_context)
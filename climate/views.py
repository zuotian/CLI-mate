"""
@organization: Leiden University Medical Center (LUMC)
@author: Zuotian Tatum
@contact: z.tatum@lumc.nl
"""
from flask import render_template, flash, url_for, redirect, request
from flask.ext.login import login_user, login_required, logout_user
from pygments import highlight
from pygments.formatters.html import HtmlFormatter

from climate import app, login_manager
from climate.forms import ToolForm, ToolUploadForm, ArgumentForm, LoginForm
from climate.models import Tool, Argument, User
from climate.utils.sw_lexer import Notation3Lexer

@app.context_processor
def view_context():
    return {
        'menu': [['About Us', 'about'],
                  ['Interface Generation', 'generate'],
                  ['Tool Definition', 'define']]}

@login_manager.user_loader
def load_user(user_id):
    if user_id != 'None':
        return User.objects.get(id=user_id)
    return None


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(csrf_enabled=True)
    if form.validate_on_submit():
        user = User(**form.data)
        if login_user(user):
            flash("Logged in successfully.")
        else:
            flash("Wrong username or password. Please try again.")
        return redirect(request.args.get('next') or url_for('index'))
    else:
        return render_template('auth/login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register')
def register():
    pass

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
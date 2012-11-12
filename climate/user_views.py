"""
@organization: Leiden University Medical Center (LUMC)
@author: Zuotian Tatum
@contact: z.tatum@lumc.nl
"""

from flask import url_for, flash, request, render_template, redirect, Blueprint
from flask.ext.login import login_user, login_required, logout_user

from climate.forms import LoginForm, RegistrationForm
from climate.models import User



user_blueprint = Blueprint('user', 'user', template_folder='templates')

@user_blueprint.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm(csrf_enabled=True)
    if form.validate_on_submit():
        try:
            user = User.objects.get(username=form.data['username'], password=form.data['password'])
            if login_user(user):
                flash("Logged in successfully.")
            return redirect(request.args.get('next') or url_for('index'))
        except User.DoesNotExist:
            form.errors['__all__'] = "Wrong username or password. Please try again."
    return render_template('auth/login.html', form=form)

@user_blueprint.route('/logout/')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@user_blueprint.route('/register/', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(csrf_enabled=True)
    if form.validate_on_submit():
        user = User(**form.data)
        user.save()
        return redirect(request.args.get('next') or url_for('index'))
    return render_template('auth/registration.html', form=form)

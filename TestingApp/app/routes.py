from flask import render_template
from app import app
from app.forms import LoginForm
from flask import render_template, flash, redirect, url_for
from flask import request
from werkzeug.urls import url_parse
from flask_login import current_user, login_user
from flask_login import logout_user
from flask_login import login_required
from app.models import User, Unit
from app import db
from app.forms import RegistrationForm


@app.route('/dashbord')
@login_required
def dashboard():
    user = User.query.filter_by(username=current_user.username).first_or_404()
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template('dashboard.html', title='Home', user=user, posts=posts)

@app.route('/enrolment')
@login_required
def enrolment():
    units = Unit.query.all()
    return render_template('enrolment.html', units=units)


@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('dashboard'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('dashboard')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/profile/<username>')
@login.login_required
def profile(username):
    user = User.query.filter_by(username = username).first_or_404
    test_completed = TestComplete.query.filter_by(user_id = user.id)
    # enrolled_units = Unit.query.filter_by(students = user.id)
    return render_template('profile.html', title = 'profile', user = user, test_completed = test_completed )

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashbord'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)



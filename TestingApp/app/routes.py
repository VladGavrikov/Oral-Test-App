from flask import render_template
from app import app
from app.forms import LoginForm
from flask import render_template, flash, redirect, url_for
from flask import request
from werkzeug.urls import url_parse
from flask_login import current_user, login_user
from flask_login import logout_user
from flask_login import login_required
from app.models import User, Unit, Test, Question
from app import db
from app.forms import RegistrationForm
from app.forms import CreateUnitForm
from app.forms import CreateQuestionForm
from app.forms import CreateTestForm
from app.forms import CreateAnswerForm

@app.route('/dashboard')
@login_required
def dashboard():
    user = User.query.filter_by(username=current_user.username).first_or_404()  
    test = Test.query.first()
    return render_template('dashboard.html', title='Dashboard', user=user, test = test)

@app.route('/attempt/<test>/<studentNumber>')
@login_required
def attempt(test, studentNumber):
    user = User.query.filter_by(username=current_user.username).first_or_404()  
    testQ = Test.query.filter_by(id=test).first()
    return render_template('testInProgress.html', title='Test', user=user, test = testQ)

@app.route('/attempt/<test>/<studentNumber>/<questionNumber>', methods=['GET', 'POST'])
@login_required
def testQuestion(test, studentNumber, questionNumber):
    user = User.query.filter_by(username=current_user.username).first_or_404()
    questions = Question.query.filter_by(test_id = test).all()
    qnumb = int(questionNumber)-1
    form = CreateAnswerForm()
    if form.validate_on_submit():
        if ((qnumb+1) == len(questions)):
            return render_template('testSubmittedSuccess.html')
        else: 
            qnumber = int(questionNumber)+1
            print(questionNumber)
            return redirect(url_for('testQuestion',test = test, studentNumber = user.id, questionNumber = qnumber))
    return render_template('answer.html', user=user, question = questions[qnumb], questionNumber = questionNumber, form = form)

@app.route('/unitManager', methods=['GET', 'POST'])
@login_required
def unitManager():
    user = User.query.filter_by(username=current_user.username).first_or_404()
    if(user.isTeacher==False):
        return redirect(url_for('dashboard'))
    else:
        form = CreateUnitForm()
        if form.validate_on_submit():
            unit = Unit(name=form.name.data, description=form.description.data)
            db.session.add(unit)
            db.session.commit()
            return redirect(url_for('unitManager'))
        units = Unit.query.all()
        return render_template('unitManager.html', units=units,form=form)

@app.route('/testCreated/<test>', methods=['GET', 'POST'])
@login_required
def testCreated(test):
    createdTest = Test.query.filter_by(id=test).first()
    createdTest.isFinalized = True
    db.session.commit()
    return render_template('testCreationSuccess.html')

@app.route('/enrolment')
@login_required
def enrolment():
    units = Unit.query.all()
    return render_template('enrolment.html', units=units)

@app.route('/<test>/<studentID>')
@login_required
def TestStart(test,user):
    questions = Question.query.filter_by(unit_id=test.id).all()
    units = Unit.query.all()
    return render_template('enrolment.html', units=units)

@app.route("/unitManager/<unitpage>", methods=['GET', 'POST'])
def unitpage(unitpage):
    unit = Unit.query.filter_by(name=unitpage).first()
    tests = Test.query.filter_by(unit_id=unitpage).all()
    testForm = CreateTestForm()
    if testForm.validate_on_submit():
        test = Test(body =testForm.name.data,unit_id=unit.name)
        db.session.add(test)
        db.session.commit()
    return render_template('unitpage.html', unit=unit,form=testForm, tests=tests)

@app.route("/unitManager/<unitpage>/<test>", methods=['GET', 'POST'])
def test(unitpage, test):
    unit = Unit.query.filter_by(name=unitpage).first()
    questions = Question.query.filter_by(test_id=test).all()
    questionForm = CreateQuestionForm()
    if questionForm.validate_on_submit():
        question = Question(questiontext =questionForm.name.data,test_id=test)
        db.session.add(question)
        db.session.commit()
    return render_template('test.html',unit=unit, form=questionForm, questions=questions, test = test)

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



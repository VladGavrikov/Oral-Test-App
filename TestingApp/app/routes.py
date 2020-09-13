from flask import render_template
from app import app
from app.forms import LoginForm
from flask import render_template, flash, redirect, url_for
from flask import Flask
from flask import request
from werkzeug.urls import url_parse
from flask_login import current_user, login_user
from flask_login import logout_user
from flask_login import login_required
from app.models import User, Unit, Test, Question, Answer, TestMark, Feedback
from app import db
from app.forms import RegistrationForm
from app.forms import CreateUnitForm
from app.forms import CreateQuestionForm
from app.forms import CreateTestForm
from app.forms import CreateAnswerForm
from app.forms import StartTest
from app.forms import CreateFeedbackForm
from app.forms import TestEvaluationForm
from app.forms import ReleaseFeedbackForm
from datetime import datetime

@app.route('/dashboard')
@login_required
def dashboard():
    user = User.query.filter_by(email=current_user.email).first_or_404()
    unit = Unit.query.filter_by(name=user.unit_id).first()
    testFB = TestMark.query.filter_by(unit_id=user.unit_id).filter_by(user_id = user.id).all()
    test = Test.query.join(TestMark).filter_by(unit_id=user.unit_id).filter_by(user_id = user.id).all()
    print(test)
    return render_template('dashboard.html', title='Dashboard', user=user, tests = test, testFB = testFB, unit=unit)

@app.route('/attempt/<test>/<studentNumber>', methods=['GET', 'POST'])
@login_required
def attempt(test, studentNumber):
    user = User.query.filter_by(email=current_user.email).first_or_404()  
    testQ = Test.query.filter_by(id=test).first()
    testAttempted = TestMark.query.filter_by(test_id=test).filter_by(user_id =user.id).first()
    form = StartTest()
    if form.validate_on_submit():
        #markFB = TestMark(user_id=user.id, test_id=int(test)) 
        #db.session.add(markFB)
        #db.session.commit()
        testAttempted.testWasStarted = True 
        db.session.commit()
        return redirect(url_for('testQuestion',test = test, studentNumber = user.id, questionNumber = 1))
    return render_template('testInProgress.html', title='Test', user=user, test = testQ ,form=form)


@app.route('/feedback/<test>/<studentNumber>', methods=['GET', 'POST'])
@login_required
def viewFeedback(test, studentNumber):
    user = User.query.filter_by(email=current_user.email).first_or_404()  
    questions = Question.query.filter_by(test_id=test).all()
    testQ = Test.query.filter_by(id=test).first()
    testMarks = TestMark.query.filter_by(user_id = studentNumber).filter_by(test_id = test).first()
    feedbacks = []
    numOfQuestions = len(questions)
    answers = []
    for question in questions:
        tempAnswer = Answer.query.filter_by(user_id=user.id).filter_by(question_id=question.id).first()
        answers.append(tempAnswer)
        feedbacks.append(Feedback.query.filter_by(answer_id = tempAnswer.id).order_by(Feedback.id.desc()).first())
    return render_template('viewFeedback.html', title='Test', user=user, questions = questions,answers=answers, test=testQ, numOfQuestions = numOfQuestions, feedbacks = feedbacks, testMarks = testMarks)



@app.route('/marking/<test>')
@login_required
def markings(test):
    tests = TestMark.query.filter_by(test_id=test).all()
    return render_template('allTestsForMarking.html', title='Test', tests = tests)

@app.route('/releaseFeedback/<test>', methods=['GET', 'POST'])
@login_required
def releaseFeedback(test):
    form = ReleaseFeedbackForm()
    tests = TestMark.query.filter_by(test_id=test).all()
    if form.validate_on_submit():
        for test in tests: 
            test.feedbackReleased = True
            db.session.commit()
            flash('Feedback has been released')
            return redirect(url_for('unitManager'))
    return render_template('releaseFeedback.html', form = form)

@app.route('/evaluation/<test>/<studentNumber>', methods=['GET', 'POST'])
@login_required
def testEvaluation(test, studentNumber):
    testMarking = TestMark.query.filter_by(test_id=test).filter_by(user_id = studentNumber).first()
    form = TestEvaluationForm()
    if form.validate_on_submit():
        testMarking.hasBeenMarked = True
        testMarking.mark1 = form.mark1.data
        testMarking.mark2 = form.mark2.data
        testMarking.mark3 = form.mark3.data
        testMarking.mark4 = form.mark4.data
        db.session.commit()
        return render_template('testHasBeenMarked.html')
    return render_template('testEvaluation.html', form = form)

@app.route('/attempt/<test>/<studentNumber>/<questionNumber>', methods=['GET', 'POST'])
@login_required
def testQuestion(test, studentNumber, questionNumber):
    user = User.query.filter_by(email=current_user.email).first_or_404()
    questions = Question.query.filter_by(test_id = test).all()
    qnumb = int(questionNumber)-1
    prefix = "app/"
    path = "/static/music/ID"+studentNumber+"Test"+test+"QNum"+questionNumber+".wav"
    form = CreateAnswerForm()
    submission = TestMark.query.filter_by(user_id = user.id).filter_by(test_id=test).first()
    if request.method == "POST" or form.validate_on_submit():
        if 'audio_data' in request.files:
            print("posted")
            f = request.files['audio_data']
            with open((prefix+path), 'wb') as audio:
                f.save(audio)
            flash("File was successfully uploaded")
        if ((qnumb+1) == len(questions)):
            print("1")
            answer = Answer(body=path, question_id=questions[qnumb].id, user_id = user.id)
            submission.due_date = datetime.now().date()
            submission.due_time = datetime.now().time()
            db.session.add(answer)
            db.session.commit()
            print("dbcommited")
            return render_template('testSubmittedSuccess.html')

        else: 
            print("2")
            answer = Answer(body=path, question_id=questions[qnumb].id, user_id = user.id)
            db.session.add(answer)
            db.session.commit()
            qnumber = int(questionNumber)+1
            print(questionNumber)
            return redirect(url_for('testQuestion',test = test, studentNumber = user.id, questionNumber = qnumber))
    return render_template('answer.html',test = test, user=user, question = questions[qnumb], questionNumber = questionNumber, form = form, numbOfQuestions = len(questions))

#FUTURE WORKS MARKING
@app.route('/marking/<test>/<studentNumber>/<questionNumber>', methods=['GET', 'POST'])
@login_required
def markingTest(test, studentNumber, questionNumber):
    user = User.query.filter_by(email=current_user.email).first_or_404()
    questions = Question.query.filter_by(test_id = test).all()
    print(questions)
    qnumb = int(questionNumber)-1
    prefix = "app/"
    path = "/static/music/ID"+studentNumber+"Test"+test+"QNum"+questionNumber+"FB"+".wav"
    answerToQuestion = Answer.query.filter_by(user_id = studentNumber).filter_by(question_id=questions[qnumb].id).first()
    print("QUESTION ID",questions[qnumb].id)
    print(answerToQuestion)
    form = CreateFeedbackForm()
    testTime = Test.query.filter_by(id = test).first()
    submissionTime = TestMark.query.filter_by(user_id = studentNumber).filter_by(test_id=test).first()
    if(submissionTime.due_date <= testTime.due_date):
        if(submissionTime.due_time <= testTime.due_time):
            submissionInTime = True
        else:
            submissionInTime = False
    else:
            submissionInTime = False
    if request.method == "POST" or form.validate_on_submit():
        if 'audio_data' in request.files:
            print("posted")
            f = request.files['audio_data']
            with open((prefix+path), 'wb') as audio:
                f.save(audio)
            flash("File was successfully uploaded")
        if ((qnumb+1) == len(questions)):
            feedback = Feedback(body=form.body.data, path=path, question_id=questions[qnumb].id, answer_id = answerToQuestion.id)
            db.session.add(feedback)
            db.session.commit()
            return redirect(url_for('testEvaluation',test = test, studentNumber = studentNumber))
            #return render_template('testHasBeenMarked.html')
        else: 
            feedback = Feedback(body=form.body.data, path=path, question_id=questions[qnumb].id, answer_id = answerToQuestion.id)
            db.session.add(feedback)
            db.session.commit()
            qnumber = int(questionNumber)+1
            print(questionNumber)
            return redirect(url_for('markingTest',test = test, studentNumber = studentNumber, questionNumber = qnumber))
    return render_template('feedback.html', user=user, question = questions[qnumb], questionNumber = questionNumber, form = form, answerToQuestion = answerToQuestion, submissionInTime= submissionInTime)

@app.route('/unitManager', methods=['GET', 'POST'])
@login_required
def unitManager():
    user = User.query.filter_by(email=current_user.email).first_or_404()
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
    usersDoingUnit = User.query.filter_by(unit_id=createdTest.unit_id).all()
    for user in usersDoingUnit:
        markFB = TestMark(user_id=user.id, test_id=int(test),unit_id = createdTest.unit_id) 
        db.session.add(markFB)
        db.session.commit()
    createdTest.isFinalized = True
    db.session.commit()
    return render_template('testCreationSuccess.html')

@app.route('/enrolment/<unit>', methods=['GET', 'POST'])
@login_required
def unitEnrolled(unit):
    user = User.query.filter_by(email=current_user.email).first_or_404()
    user.unit_id = unit
    db.session.commit()
    return render_template('unitEnrollmentSuccess.html')
    

@app.route('/enrolment')
@login_required
def enrolment():
    units = Unit.query.all()
    user = User.query.filter_by(email=current_user.email).first_or_404()
    return render_template('enrolment.html', units=units, user=user)

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
        test = Test(body =testForm.name.data,due_date=testForm.due_date.data,due_time=testForm.due_time.data,unit_id=unit.name)
        db.session.add(test)
        db.session.commit()
        return redirect(url_for('unitpage',unitpage = unit.name))
    return render_template('unitpage.html', unit=unit,form=testForm, tests=tests)

@app.route("/unitManager/<unitpage>/ManageStudents", methods=['GET', 'POST'])
def manageStudents(unitpage):
    unit = Unit.query.filter_by(name=unitpage).first()
    students = User.query.filter_by(unit_id = unit.name).all()
    return render_template('manageStudents.html', unit=unit, students=students)

@app.route("/unitManager/<unitpage>/<test>", methods=['GET', 'POST'])
def test(unitpage, test):
    unit = Unit.query.filter_by(name=unitpage).first()
    t = Test.query.filter_by(id=test).first()
    questions = Question.query.filter_by(test_id=test).all()
    questionForm = CreateQuestionForm()
    if questionForm.validate_on_submit():
        question = Question(body =repr(questionForm.name.data.encode())[2:-1],test_id=test)
        db.session.add(question)
        db.session.commit()
        return redirect(url_for('test', unitpage = unit.name, test= test))
    return render_template('test.html',unit=unit, form=questionForm, questions=questions, test = test, t = t)

@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('dashboard'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            if (user.isTeacher == False):
                next_page = url_for('dashboard')
            else:
                next_page = url_for('unitManager')
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
        user = User(id=form.studentNumber.data, email=form.email.data, firstName= form.firstName.data, LastName = form.lastName.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)



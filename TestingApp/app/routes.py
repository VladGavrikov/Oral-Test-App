from flask import render_template
from app import app
from app.forms import LoginForm
from flask import render_template, flash, redirect, url_for
from flask import Flask, json
import tempfile
from flask import request
from werkzeug.urls import url_parse
from flask_login import current_user, login_user
from flask_login import logout_user
from flask_login import login_required
from app.models import User, Unit, Test, Question, Answer, TestMark, Feedback
from app import db
from app.forms import RegistrationForm, CreateUnitForm, CreateQuestionForm, CreateTestForm, CreateAnswerForm, StartTest, CreateFeedbackForm, TestEvaluationForm, TestEvaluationForm, ReleaseFeedbackForm, RenameTestForm

# from app.forms import RegistrationForm
# from app.forms import CreateUnitForm
# from app.forms import CreateQuestionForm
# from app.forms import CreateTestForm
# from app.forms import CreateAnswerForm
# from app.forms import StartTest
# from app.forms import CreateFeedbackForm
# from app.forms import TestEvaluationForm
# from app.forms import ReleaseFeedbackForm
from datetime import datetime
import numpy as np
import os.path
from random import randint

import io
import csv
from flask import make_response

@app.route('/dashboard')
@login_required
def dashboard():
    user = User.query.filter_by(email=current_user.email).first_or_404()
    if(user.isTeacher==True):
        return redirect(url_for('unitManager'))
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


@app.route('/feedback/<test>/<studentNumber>/<questionNumber>', methods=['GET', 'POST'])
@login_required
def viewFeedback(test, studentNumber, questionNumber):
    units = Unit.query.all()
    user = User.query.filter_by(email=current_user.email).first_or_404()  
    unit  = Unit.query.filter_by(name=current_user.unit_id).first_or_404()  
    questions = Question.query.filter_by(test_id=test).all()
    print(questions)
    questionNumber = int(questionNumber)
    testQ = Test.query.filter_by(id=test).first()
    testMarks = TestMark.query.filter_by(user_id = studentNumber).filter_by(test_id = test).first()
    feedbacks = []
    numOfQuestions = len(questions)
    answers = []
    import parselmouth
    data="[-1.0]"
    data2="[-1.0]"
    tempAnswer = Answer.query.filter_by(user_id=user.id).filter_by(question_id=questions[questionNumber-1].id).first()
    answers.append(tempAnswer)
    if(tempAnswer==None):
        tempFeedback=None
    else:
        tempFeedback = Feedback.query.filter_by(answer_id = tempAnswer.id).order_by(Feedback.id.desc()).first()
    feedbacks.append(tempFeedback)
    if(tempAnswer!=None):
        if(tempAnswer.body!="empty"):
            print(tempAnswer.body)
            string = tempAnswer.body
            sep = '?noCache='
            separated = string.split(sep, 1)[0]
            sound = parselmouth.Sound("app"+separated)
            print(separated)
            pitch_track = sound.to_pitch().selected_array['frequency']
            data = json.dumps(pitch_track.tolist())
    if(tempFeedback!=None):
        if(tempFeedback.path!="empty"):
            string2= tempFeedback.path
            sep2 = '?noCache='
            separated2 = string2.split(sep2, 1)[0]
            sound2 = parselmouth.Sound("app"+separated2)
            pitch_track2 = sound2.to_pitch().selected_array['frequency']
            data2 = json.dumps(pitch_track2.tolist())
    print("TEMPANSWER", tempAnswer)
    return render_template('viewFeedback.html', units=units, title='Feedback', user=user, questions = questions,answers=answers, test=testQ, numOfQuestions = numOfQuestions, feedbacks = feedbacks, testMarks = testMarks, data = data, data2 = data2, unit = unit, questionNumber = questionNumber, testPassed = test)


@app.route('/marking/<test>', methods=['GET', 'POST'])
@login_required
def markings(test):
    units = Unit.query.all()
    tests = TestMark.query.filter_by(test_id=test).all()
    form = ReleaseFeedbackForm()
    tests = TestMark.query.filter_by(test_id=test).all()
    testsFiltered = []
    for test in tests: 
        enrolledStudent = User.query.filter_by(id=test.user_id).first()
        if(test.unit_id==enrolledStudent.unit_id):
            testsFiltered.append(test)
    tests = testsFiltered
    print("FILTERED TESTS:",tests)
    if form.validate_on_submit():
        for test in tests: 
            test.feedbackReleased = True
            db.session.commit()
        # flash('Feedback has been released')
        return redirect(url_for('unitManager'))
    return render_template('allTestsForMarking.html', title='Marking', tests = tests, form=form,units=units)

@app.route('/unenroll/<studentNumber>')
@login_required
def unenroll(studentNumber):
    user = User.query.filter_by(id = studentNumber).first()
    unenrollStudent = TestMark.query.filter_by(unit_id=user.unit_id).filter_by(user_id=user.id).all()
    print("UNENROLLING FROM: ",unenrollStudent)
    for test in unenrollStudent: 
        db.session.delete(test)
    units = Unit.query.all()
    user.unit_id = None
    db.session.commit()
    return render_template('studentUnenrolledSuccess.html', title='Unenroll', units =units)


# @app.route('/releaseFeedback/<test>', methods=['GET', 'POST'])
# @login_required
# def releaseFeedback(test):
#     form = ReleaseFeedbackForm()
#     tests = TestMark.query.filter_by(test_id=test).all()
#     if form.validate_on_submit():
#         for test in tests: 
#             test.feedbackReleased = True
#             db.session.commit()
#             flash('Feedback has been released')
#             return redirect(url_for('unitManager'))
#     return render_template('releaseFeedback.html', form = form)

@app.route('/evaluation/<test>/<studentNumber>', methods=['GET', 'POST'])
@login_required
def testEvaluation(test, studentNumber):
    units = Unit.query.all()
    testMarking = TestMark.query.filter_by(test_id=test).filter_by(user_id = studentNumber).first()
    user = User.query.filter_by(id=studentNumber).first_or_404()
    unit = Unit.query.filter_by(name=user.unit_id).first_or_404()
    testQ = Test.query.filter_by(id=test).first()
    form = TestEvaluationForm()
    submittionDate = testMarking.due_date
    submittionTime = testMarking.due_time
    due_date = testQ.due_date
    due_time = testQ.due_time
    submissionInTime = None
    if(submittionDate ==None or submittionTime == None):
        testWasntSubmitted = True
    else:
        if(submittionDate <= due_date):
            if(submittionTime <= due_time):
                submissionInTime = True
            else:
                submissionInTime = False
        else:
                submissionInTime = False
    if form.validate_on_submit():
        testMarking.hasBeenMarked = True
        testMarking.mark1 = form.mark1.data
        testMarking.mark2 = form.mark2.data
        testMarking.mark3 = form.mark3.data
        testMarking.mark4 = form.mark4.data
        testMarking.testWasStarted = True
        db.session.commit()
        return render_template('testHasBeenMarked.html',units = units)
    return render_template('testEvaluation.html', title='Evaluation', form = form, unit=unit,units=units, submissionInTime=submissionInTime, submittionDate = submittionDate, submittionTime =submittionTime,
                                                        due_date=due_date, due_time=due_time)

@app.route('/attempt/<test>/<studentNumber>/<questionNumber>', methods=['GET', 'POST'])
@login_required
def testQuestion(test, studentNumber, questionNumber):
    user = User.query.filter_by(email=current_user.email).first_or_404()
    questions = Question.query.filter_by(test_id = test).all()
    qnumb = int(questionNumber)-1
    prefix = "app/"
    path = "/static/music/ID"+studentNumber+"Test"+test+"QNum"+questionNumber+".wav"
    randomNumber = randint(0, 10000000000)
    pathtoPage = "/static/music/ID"+studentNumber+"Test"+test+"QNum"+questionNumber+".wav"+"?noCache="+str(randomNumber)
    form = CreateAnswerForm()
    submission = TestMark.query.filter_by(user_id = user.id).filter_by(test_id=test).first()
    successfullySubmitted = False
    lastQuestion = False
    if request.method == "POST" or form.validate_on_submit():
        if 'audio_data' in request.files:
            print("posted")
            f = request.files['audio_data']
            with open((prefix+path), 'wb') as audio:
                f.save(audio)
            successfullySubmitted = True
            print(successfullySubmitted)
            print("Redirect start")
        if ((qnumb+1) == len(questions)):
            lastQuestion=False
            print("1")
            if(successfullySubmitted):
                answer = Answer(body=pathtoPage, question_id=questions[qnumb].id, user_id = user.id)
            else:
                answer = Answer(body="empty", question_id=questions[qnumb].id, user_id = user.id)
            submission.due_date = datetime.now().date()
            submission.due_time = datetime.now().time()
            db.session.add(answer)
            db.session.commit()
            print("dbcommited")
            return render_template('testSubmittedSuccess.html')

        else: 
            print("2")
            LastQuestion=True
            if(successfullySubmitted):
                answer = Answer(body=pathtoPage, question_id=questions[qnumb].id, user_id = user.id)
            else:
                answer = Answer(body="empty", question_id=questions[qnumb].id, user_id = user.id)
            db.session.add(answer)
            db.session.commit()
            qnumber = int(questionNumber)+1
            print(questionNumber)
            return redirect(url_for('testQuestion',test = test, studentNumber = user.id, questionNumber = qnumber))
    print("Printing sS var ", successfullySubmitted)
    return render_template('answer.html', title='Test In Progress',test = test, user=user, question = questions[qnumb], questionNumber = questionNumber, form = form, numbOfQuestions = len(questions),path=pathtoPage,successfullySubmitted = successfullySubmitted)

#FUTURE WORKS MARKING
@app.route('/marking/<test>/<studentNumber>/<questionNumber>', methods=['GET', 'POST'])
@login_required
def markingTest(test, studentNumber, questionNumber):
    units = Unit.query.all()
    user = User.query.filter_by(email=current_user.email).first_or_404()
    questions = Question.query.filter_by(test_id = test).all()
    print(questions)
    qnumb = int(questionNumber)-1
    prefix = "app/"
    path = "/static/music/ID"+studentNumber+"Test"+test+"QNum"+questionNumber+"FB"+".wav"
    randomNumber = randint(0, 10000000000)
    pathtoPage = "/static/music/ID"+studentNumber+"Test"+test+"QNum"+questionNumber+"FB"+".wav"+"?noCache="+str(randomNumber)
    answerToQuestion = Answer.query.filter_by(user_id = studentNumber).filter_by(question_id=questions[qnumb].id).first()
    print("QUESTION ID",questions[qnumb].id)
    print(answerToQuestion)
    testTime = Test.query.filter_by(id = test).first()
    submissionTime = TestMark.query.filter_by(user_id = studentNumber).filter_by(test_id=test).first()
    if(submissionTime.due_date==None or submissionTime.due_time==None):
        return redirect(url_for('testEvaluation',test = test, studentNumber = studentNumber))
    if(submissionTime.due_date <= testTime.due_date):
        if(submissionTime.due_time <= testTime.due_time):
            submissionInTime = True
        else:
            submissionInTime = False
    else:
            submissionInTime = False
    if(submissionTime.hasBeenMarked==True):
        print("TEST HAS BEEN MARKED")
        storedAudio=Feedback.query.filter_by(answer_id = answerToQuestion.id).filter_by(question_id =questions[qnumb].id).order_by(Feedback.id.desc()).first().path
        print(storedAudio)
        storedText=Feedback.query.filter_by(answer_id = answerToQuestion.id).filter_by(question_id =questions[qnumb].id).order_by(Feedback.id.desc()).first().body
    else:
        storedAudio = "empty"
        storedText = None
    person = {'body': storedText }
    form = CreateFeedbackForm(data=person)
    if request.method == "POST" or form.validate_on_submit():
        if 'audio_data' in request.files:
            print("posted")
            f = request.files['audio_data']
            with open((prefix+path), 'wb') as audio:
                f.save(audio)
            # flash("File was successfully uploaded")
        if ((qnumb+1) == len(questions)):
            if(os.path.isfile(prefix+path)):
                feedback = Feedback(body=form.body.data, path=pathtoPage, question_id=questions[qnumb].id, answer_id = answerToQuestion.id)
            else:
                feedback = Feedback(body=form.body.data, path="empty", question_id=questions[qnumb].id, answer_id = answerToQuestion.id)
            db.session.add(feedback)
            db.session.commit()
            return redirect(url_for('testEvaluation',test = test, studentNumber = studentNumber))
            #return render_template('testHasBeenMarked.html')
        else: 
            if(os.path.isfile(prefix+path)):
                feedback = Feedback(body=form.body.data, path=pathtoPage, question_id=questions[qnumb].id, answer_id = answerToQuestion.id)
            else:
                feedback = Feedback(body=form.body.data, path="empty", question_id=questions[qnumb].id, answer_id = answerToQuestion.id)
            db.session.add(feedback)
            db.session.commit()
            qnumber = int(questionNumber)+1
            print(questionNumber)
            return redirect(url_for('markingTest',test = test, studentNumber = studentNumber, questionNumber = qnumber))
    return render_template('feedback.html', title='Marking In Progress',units=units, user=user,questions=questions, question = questions[qnumb], questionNumber = qnumb, form = form, answerToQuestion = answerToQuestion, submissionInTime= submissionInTime, path=pathtoPage,test=submissionTime, storedAudio =storedAudio, storedText=storedText)

@app.route('/unitManager', methods=['GET', 'POST'])
@login_required
def unitManager():
    user = User.query.filter_by(email=current_user.email).first_or_404()
    if(user.isTeacher==False):
        return redirect(url_for('dashboard'))
    else:
        form = CreateUnitForm()
        if form.validate_on_submit():
            unit = Unit(name=form.name.data, description=form.description.data, mark1Criteria=form.mark1Criteria.data,mark2Criteria=form.mark2Criteria.data,mark3Criteria=form.mark3Criteria.data,mark4Criteria=form.mark4Criteria.data)
            db.session.add(unit)
            db.session.commit()
            return redirect(url_for('unitManager'))
        units = Unit.query.all()
        return render_template('unitManager.html', title='Unit Manager', units=units,form=form)

@app.route('/testCreated/<test>', methods=['GET', 'POST'])
@login_required
def testCreated(test):
    createdTest = Test.query.filter_by(id=test).first()
    questions = Question.query.filter_by(test_id = test).all()
    usersDoingUnit = User.query.filter_by(unit_id=createdTest.unit_id).all()
    units = Unit.query.all()
    if(len(questions)==0):
        return render_template('testCreationFailure.html',test =test, unitpage=createdTest.unit_id, units=units)
    else:
        for user in usersDoingUnit:
            markFB = TestMark(user_id=user.id, test_id=int(test),unit_id = createdTest.unit_id) 
            db.session.add(markFB)
            db.session.commit()
        createdTest.isFinalized = True
        db.session.commit()
    return render_template('testCreationSuccess.html', title='Test Created', units=units)

@app.route('/enrolment/<unit>', methods=['GET', 'POST'])
@login_required
def unitEnrolled(unit):
    user = User.query.filter_by(email=current_user.email).first_or_404()
    user.unit_id = unit
    tests = Test.query.filter_by(unit_id=unit).all()
    
    for test in tests:
        newEnrollment = TestMark.query.filter_by(unit_id=unit).filter_by(user_id = user.id).filter_by(test_id = test.id).all()
        print(newEnrollment)
        if(len(newEnrollment)==0):
            markFB = TestMark(user_id=user.id, test_id=test.id,unit_id = unit)
            db.session.add(markFB)
    db.session.commit()
    return render_template('unitEnrollmentSuccess.html', title='Enrollment Success')
    

@app.route('/enrolment')
@login_required
def enrolment():
    units = Unit.query.all()
    user = User.query.filter_by(email=current_user.email).first_or_404()
    return render_template('enrolment.html', title='Enrollment', units=units, user=user)

@app.route('/<test>/<studentID>')
@login_required
def TestStart(test,user):
    questions = Question.query.filter_by(unit_id=test.id).all()
    units = Unit.query.all()
    return render_template('enrolment.html', units=units)

@app.route("/unitManager/<unitpage>", methods=['GET', 'POST'])
def unitpage(unitpage):
    units = Unit.query.all()
    unit = Unit.query.filter_by(name=unitpage).first()
    tests = Test.query.filter_by(unit_id=unitpage).all()
    testmark = TestMark.query.filter_by(unit_id=unitpage).all()
    testForm = CreateTestForm()
    if testForm.validate_on_submit():
        test = Test(body =testForm.name.data,due_date=testForm.due_date.data,due_time=testForm.due_time.data,unit_id=unit.name)
        db.session.add(test)
        db.session.commit()
        return redirect(url_for('unitpage',unitpage = unit.name))
    return render_template('unitpage.html', title='Unit Page', unit=unit,form=testForm, tests=tests, testmark = testmark, units = units)

@app.route("/unitManager/<unitpage>/<test>/feedback", methods=['GET', 'POST'])
@login_required
def feedback(unitpage, test):
    units = Unit.query.all()
    #test = Test.query.join(TestMark).filter_by(unit_id=user.unit_id).filter_by(user_id = user.id).all()
    #join(TestMark).filter_by(unit_id=user.unit_id)
    #testmarks = TestMark.query.filter_by(test_id = test).join(User, User.id==TestMark.user_id).all()
    testmarks = db.session.query(User, TestMark).outerjoin(TestMark, User.id==TestMark.user_id).filter_by(test_id=test).filter_by(unit_id=User.unit_id).order_by(User.LastName).all()
    return render_template('feedbackTeacher.html', title='Feedback', testmarks = testmarks, units=units)

@app.route("/unitManager/<unitpage>/<test>/feedbackDownload", methods=['GET', 'POST'])
@login_required
def feedbackDownload(unitpage, test):
    testmarks = db.session.query(User, TestMark).outerjoin(TestMark, User.id==TestMark.user_id).filter_by(test_id=test).order_by(User.LastName).all()
    test = Test.query.filter_by(id=test).first()
    csv = ''
    print(testmarks)
    csv = csv +("Last Name,First Name,StudentNumber,Mark\n")
    for testmark in testmarks:
        print(testmark)
        if(testmark[1].mark1==None or testmark[1].mark2==None or testmark[1].mark3==None or testmark[1].mark4==None):
            csv = csv +(testmark[0].LastName +","+testmark[0].firstName+","+str(testmark[0].id)+",0\n")
        else:
            csv = csv +(testmark[0].LastName +","+testmark[0].firstName+","+str(testmark[0].id)+","+str(testmark[1].mark1+testmark[1].mark2+testmark[1].mark3+testmark[1].mark4)+"\n")
    response = make_response(csv)
    cd = 'attachment; filename='+unitpage+test.body+'FB.csv'
    response.headers['Content-Disposition'] = cd 
    response.mimetype='text/csv'

    return response

@app.route("/unitManager/<unitpage>/ManageStudents", methods=['GET', 'POST'])
def manageStudents(unitpage):
    unit = Unit.query.filter_by(name=unitpage).first()
    units = Unit.query.all()
    students = User.query.filter_by(unit_id = unit.name).all()
    return render_template('manageStudents.html', unit=unit, students=students, units=units)

@app.route("/unitManager/<unitpage>/<test>", methods=['GET', 'POST'])
def test(unitpage, test):
    units = Unit.query.all()
    unit = Unit.query.filter_by(name=unitpage).first()
    t = Test.query.filter_by(id=test).first()
    
    renameForm = RenameTestForm()
    if renameForm.submitRename.data and renameForm.validate_on_submit():
            t.body = renameForm.newTestName.data
            db.session.commit()
            return redirect(url_for('test', unitpage=unit.name, test=test))

    questions = Question.query.filter_by(test_id=test).all()
    questionForm = CreateQuestionForm()
    prefix = "app/"
    path = "/static/music/Test"+test+"QNum"+str(len(questions)+1)+".wav"
    randomNumber = randint(0, 10000000000)
    pathtoPage = "/static/music/Test"+test+"QNum"+str(len(questions)+1)+".wav"+"?noCache="+str(randomNumber)
    if request.method == "POST" or questionForm.validate_on_submit():
        if 'audio_data' in request.files:
            print("posted")
            f = request.files['audio_data']
            with open((prefix+path), 'wb') as audio:
                f.save(audio)
            print("File was successfully uploaded")
        if questionForm.validate_on_submit():
            if(os.path.isfile(prefix+path)):
                print("succesfully submitted true")
                question = Question(body =repr(questionForm.name.data.encode())[2:-1],path=pathtoPage,test_id=test)
            else: 
                print("succesfully submitted false")
                question = Question(body =repr(questionForm.name.data.encode())[2:-1],path="empty",test_id=test)
            db.session.add(question)
            db.session.commit()
            return redirect(url_for('test', unitpage = unit.name, test= test))
    return render_template('test.html',unit=unit, form=questionForm, renameForm=renameForm, questions=questions, test = test, t = t, units = units,path=pathtoPage)

@app.route("/unitManager/<unitpage>/<test>/delete", methods=['GET', 'POST'])
def deleteTest(unitpage, test):
    unit = Unit.query.filter_by(name=unitpage).first()
    test = Test.query.filter_by(id=test).first()

    db.session.delete(test)
    db.session.commit()

    return redirect(url_for('unitpage', unitpage = unit.name))


@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if (current_user.isTeacher == True):
            return redirect(url_for('unitManager'))
        else:
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
                print("I WAS HERE")
            else:
                next_page = url_for('unitManager')
                print("I WAS HERE!!!!!!")
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


from app.forms import ResetPasswordRequestForm
from app.email import send_password_reset_email

@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password (check Spam)')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)


from app.forms import ResetPasswordForm


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)
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
from app.forms import RegistrationForm, CreateUnitForm, CreateQuestionForm, CreateTestForm, CreateAnswerForm, StartTest, CreateFeedbackForm, TestEvaluationForm, TestEvaluationForm, ReleaseFeedbackForm, RenameTestForm, ResetDatabaseForm,DeleteQuestionForm
from datetime import datetime
import os
os.environ["OMP_NUM_THREADS"] = "1"
import numpy as np
from random import randint
from app.decorators import check_confirmed

import io
import csv
from flask import make_response


@app.route('/dashboard')
@login_required
@check_confirmed
def dashboard():
    user = User.query.filter_by(email=current_user.email).first_or_404()
    if(user.isTeacher==True):
        return redirect(url_for('unitManager'))
    if(user.unit_id==None):
        return redirect(url_for('enrolment'))
    unit = Unit.query.filter_by(name=user.unit_id).first()
    testFB = TestMark.query.filter_by(unit_id=user.unit_id).filter_by(user_id = user.id).all()
    test = Test.query.join(TestMark).filter_by(unit_id=user.unit_id).filter_by(user_id = user.id).all()
    currentDate = datetime.now().date()
    currentTime = datetime.now().time()
    print(test)
    return render_template('dashboard.html', title='Dashboard', user=user, tests = test, testFB = testFB, unit=unit, currentDate = currentDate, currentTime = currentTime)

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
    testmarksForaverage = db.session.query(User, TestMark).outerjoin(TestMark, User.id==TestMark.user_id).filter_by(test_id=test).filter_by(unit_id=User.unit_id).all()
    listOfTotalMarksForAVG = []
    for eachMarkForAverage in testmarksForaverage:
        if(eachMarkForAverage[1].mark1!=None):
            totalEachMark = eachMarkForAverage[1].mark1+eachMarkForAverage[1].mark2+eachMarkForAverage[1].mark3+eachMarkForAverage[1].mark4
        else:
            totalEachMark = 0
        listOfTotalMarksForAVG.append(totalEachMark)
        listOfTotalMarksForAVG.sort()
    if(testMarks.mark1!=None):
        totalMark = testMarks.mark1 + testMarks.mark2 + testMarks.mark3 + testMarks.mark4
    else: 
        totalMark = 0
    positionInClass= len(listOfTotalMarksForAVG)+1
    for eachIteration in listOfTotalMarksForAVG:
        if(totalMark>=eachIteration):
            positionInClass = positionInClass -1
        else: 
            break
    print("POSITION: ", positionInClass)
    avgOfTest= sum(listOfTotalMarksForAVG)/len(listOfTotalMarksForAVG)

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
    return render_template('viewFeedback.html', units=units, title='Feedback', user=user, questions = questions,answers=answers, test=testQ,
     numOfQuestions = numOfQuestions, feedbacks = feedbacks, testMarks = testMarks, data = data, data2 = data2, unit = unit, 
     questionNumber = questionNumber, testPassed = test, avgOfTest=avgOfTest, positionInClass= positionInClass, lengthOfClass=len(listOfTotalMarksForAVG))


@app.route('/marking/<test>', methods=['GET', 'POST'])
@login_required
def markings(test):
    units = Unit.query.all()
    testGeneral = Test.query.filter_by(id=test).first()

    tests = db.session.query(User, TestMark).outerjoin(TestMark, User.id==TestMark.user_id).filter_by(test_id=test).filter_by(unit_id=User.unit_id).order_by(User.LastName).all()

    t = Test.query.filter_by(id=test).first()
    form = ReleaseFeedbackForm()
    testsFiltered = []

    for test in tests: 
        enrolledStudent = User.query.filter_by(id=test[1].user_id).first()
        if(test[1].unit_id==enrolledStudent.unit_id):
            testsFiltered.append(test)
    tests = testsFiltered
    print("\n\n\n\n\n"  ,tests)
    print("FILTERED TESTS:",tests)
    if form.validate_on_submit():
        testGeneral.feedbackReleased=True
        for test in tests: 
            test[1].feedbackReleased = True
            db.session.commit()
        # flash('Feedback has been released')
        return redirect(url_for('unitManager'))
    return render_template('allTestsForMarking.html', title='Marking', tests = tests, t = t, form=form, units=units)

@app.route("/unitManager/<unitpage>/<test>/feedback", methods=['GET', 'POST'])
@login_required
def feedback(unitpage, test):
    units = Unit.query.all()
    #test = Test.query.join(TestMark).filter_by(unit_id=user.unit_id).filter_by(user_id = user.id).all()
    #join(TestMark).filter_by(unit_id=user.unit_id)
    #testmarks = TestMark.query.filter_by(test_id = test).join(User, User.id==TestMark.user_id).all()
    testmarks = db.session.query(User, TestMark).outerjoin(TestMark, User.id==TestMark.user_id).filter_by(test_id=test).filter_by(unit_id=User.unit_id).order_by(User.LastName).all()
    return render_template('feedbackTeacher.html', title='Feedback', testmarks = testmarks, units=units)

@app.route('/unenroll/<studentNumber>')
@login_required
def unenroll(studentNumber):
    user = User.query.filter_by(id = studentNumber).first()
    unenrollStudent = TestMark.query.filter_by(unit_id=user.unit_id).filter_by(user_id=user.id).all()
    print("UNENROLLING FROM: ",unenrollStudent)
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
    student = User.query.filter_by(id = studentNumber).first()
    form = TestEvaluationForm()
    submittionDate = testMarking.due_date
    submittionTime = testMarking.due_time
    due_date = testQ.due_date
    due_time = testQ.due_time
    #finding out how late submittion was
    submittedDateANDTime = datetime.combine(submittionDate,  submittionTime)
    dueDateANDTime = datetime.combine(due_date,  due_time)
    difference = submittedDateANDTime-dueDateANDTime
    days = difference.days
    seconds = difference.seconds 
    hours = seconds//3600
    minutes = (seconds//60)%60
    submissionInTime = None
    if(submittionDate ==None or submittionTime == None):
        testWasntSubmitted = True
    else:
        if(submittionDate < due_date):
            submissionInTime = True
        elif(submittionDate == due_date):
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
        return render_template('testMarkedSuccess.html',units = units, test = test)
    return render_template('testEvaluation.html', title='Evaluation', form = form, unit=unit,units=units, student = student, t = testQ, 
    submissionInTime=submissionInTime, submittionDate = submittionDate, submittionTime =submittionTime, due_date=due_date, due_time=due_time,
    days=days, hours=hours, minutes=minutes)

@app.route('/attempt/<test>/<studentNumber>/<questionNumber>', methods=['GET', 'POST'])
@login_required
def testQuestion(test, studentNumber, questionNumber):
    user = User.query.filter_by(email=current_user.email).first_or_404()
    tests = Test.query.filter_by(id=test).first()
    print(tests)
    questions = Question.query.filter_by(test_id = test).all()
    currentTest = Test.query.filter_by(id = test).first()
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
            if(currentTest.feedbackReleased):
                submission.feedbackReleased=True
            db.session.add(answer)
            db.session.commit()
            print("dbcommited")
            return render_template('testSubmittedSuccess.html', title='Test Submitted')

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
    return render_template('answer.html', title='Test In Progress',test = test, tests = tests, user = user, question = questions[qnumb], questionNumber = questionNumber, form = form, numbOfQuestions = len(questions), path=pathtoPage, successfullySubmitted = successfullySubmitted)

#FUTURE WORKS MARKING
@app.route('/marking/<test>/<studentNumber>/<questionNumber>', methods=['GET', 'POST'])
@login_required
def markingTest(test, studentNumber, questionNumber):
    units = Unit.query.all()
    user = User.query.filter_by(email=current_user.email).first_or_404()
    student = User.query.filter_by(id = studentNumber).first()
    t = Test.query.filter_by(id=test).first()
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
    print("STORED TEXT: ", storedAudio)
    storedText=Feedback.query.filter_by(answer_id = answerToQuestion.id).filter_by(question_id =questions[qnumb].id).order_by(Feedback.id.desc()).first()
    if(storedText!=None):
        storedText=storedText.body
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
    return render_template('feedback.html', title='Marking In Progress',units=units, user=user, questions=questions, question = questions[qnumb], 
    questionNumber = qnumb, form = form, answerToQuestion = answerToQuestion, submissionInTime= submissionInTime, path=pathtoPage,test=submissionTime, 
    storedAudio =storedAudio, storedText=storedText, student = student, t = t)

@app.route('/unitManager', methods=['GET', 'POST'])
@login_required
def unitManager():
    
    message = ""
    user = User.query.filter_by(email=current_user.email).first_or_404()
    if(user.isTeacher==False):
        return redirect(url_for('dashboard'))
    else:
        form = CreateUnitForm()
        formReset= ResetDatabaseForm()
        if form.validate_on_submit():
            unit = Unit(name=form.name.data, description=form.description.data, mark1Criteria=form.mark1Criteria.data,mark2Criteria=form.mark2Criteria.data,mark3Criteria=form.mark3Criteria.data,mark4Criteria=form.mark4Criteria.data)
            db.session.add(unit)
            db.session.commit()
            return redirect(url_for('unitManager'))
        if formReset.validate_on_submit():
            folder = 'app/static/music/'
            for filename in os.listdir(folder):
                dirToFile = folder+filename
                os.remove(dirToFile)
            if(formReset.passwordResetter.data=="SUPERHARDPASSWORD"): 
                users = User.query.filter_by(isTeacher=False).all()
                for user in users:
                    db.session.delete(user)
                units = Unit.query.all()
                for unit in units:
                    db.session.delete(unit)
                tests = Test.query.all()
                for test in tests:
                    db.session.delete(test)
                
                questions = Question.query.all()
                for question in questions:
                    db.session.delete(question)

                answers = Answer.query.all()
                for answer in answers:
                    db.session.delete(answer)

                feedbacks = Feedback.query.all()
                for feedback in feedbacks:
                    db.session.delete(feedback)

                testmarks = TestMark.query.all()
                for testmark in testmarks:
                    db.session.delete(testmark)
                
                db.session.commit()
                flash("Database Successfully cleaned")
                return redirect(url_for('unitManager'))
            else:
                flash("Password is incorrect")
                return redirect(url_for('unitManager'))
        units = Unit.query.all()
        return render_template('unitManager.html', title='Unit Manager', units=units,form=form, formReset=formReset)

@app.route('/testCreated/<test>', methods=['GET', 'POST'])
@login_required
def testCreated(test):
    createdTest = Test.query.filter_by(id=test).first()
    questions = Question.query.filter_by(test_id = test).all()
    usersDoingUnit = User.query.filter_by(unit_id=createdTest.unit_id).all()
    units = Unit.query.all()
    if(len(questions)==0):
        return render_template('testCreationFailure.html', title='Empty Task', test = test, unitpage = createdTest.unit_id, units = units)
    else:
        for user in usersDoingUnit:
            markFB = TestMark(user_id=user.id, test_id=int(test),unit_id = createdTest.unit_id) 
            db.session.add(markFB)
            db.session.commit()
        createdTest.isFinalized = True
        db.session.commit()
    return render_template('testCreationSuccess.html', title='Test Created', units = units, currentunit = createdTest.unit_id)

@app.route('/enrolment/<unit>', methods=['GET', 'POST'])
@login_required
@check_confirmed
def unitEnrolled(unit):
    user = User.query.filter_by(email=current_user.email).first_or_404()
    user.unit_id = unit
    tests = Test.query.filter_by(unit_id=unit).all()
    
    for test in tests:
        newEnrollment = TestMark.query.filter_by(unit_id=unit).filter_by(user_id = user.id).filter_by(test_id = test.id).all()
        print(newEnrollment)
        if(len(newEnrollment)==0):
            if(test.isFinalized):
                markFB = TestMark(user_id=user.id, test_id=test.id,unit_id = unit)
                db.session.add(markFB)
    db.session.commit()
    return render_template('unitEnrollmentSuccess.html', title='Enrolment Success')
    

@app.route('/enrolment')
@check_confirmed
@login_required
def enrolment():
    units = Unit.query.all()
    user = User.query.filter_by(email=current_user.email).first_or_404()
    return render_template('enrolment.html', title='Enrolment', units=units, user=user)

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
    tests = Test.query.filter_by(unit_id=unitpage).order_by(Test.due_date.desc(), Test.due_time.desc()).all()
    testmark = TestMark.query.filter_by(unit_id=unitpage).all()
    testForm = CreateTestForm()
    if testForm.validate_on_submit():
        test = Test(body =testForm.name.data,due_date=testForm.due_date.data,due_time=testForm.due_time.data,unit_id=unit.name)
        db.session.add(test)
        db.session.commit()
        return redirect(url_for('unitpage',unitpage = unit.name))
    return render_template('unitpage.html', title='Unit Page', unit=unit,form=testForm, tests=tests, testmark = testmark, units = units)

@app.route("/unitManager/<unitpage>/<test>/feedbackDownload", methods=['GET', 'POST'])
@login_required
def feedbackDownload(unitpage, test):
    testmarks = db.session.query(User, TestMark).outerjoin(TestMark, User.id==TestMark.user_id).filter_by(test_id=test).filter_by(unit_id=User.unit_id).order_by(User.LastName).all()
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

@app.route("/unitManager/<unitpage>/<test>/<questionNumber>", methods=['GET', 'POST'])
def test(unitpage, test,questionNumber):
    units = Unit.query.all()
    unit = Unit.query.filter_by(name=unitpage).first()
    t = Test.query.filter_by(id=test).first()

    renameForm = RenameTestForm()
    if renameForm.submitRename.data and renameForm.validate_on_submit():
            t.body = renameForm.newTestName.data
            db.session.commit()
            return redirect(url_for('test', unitpage=unit.name, test=test, questionNumber=questionNumber))

    questions = Question.query.filter_by(test_id=test).all()
    eachQuestion = None
    if(questions!=[]):
        questions.append("")
        print("QUESTION", questions)
        eachQuestion = questions[int(questionNumber)-1]
    if(eachQuestion!="" and eachQuestion!=None):
        storedText=eachQuestion.body
    else:
        storedText=None
    deleteForm = DeleteQuestionForm()
    print("STORED TEXT: ",storedText)
    person = {'name': storedText }
    questionForm = CreateQuestionForm(data=person)
    if deleteForm.submitDelete.data and  deleteForm.validate_on_submit():
        print("fn Delete form")
        print("EACH QUESTION:",eachQuestion)
        if(os.path.isfile("app/static/music/Test"+test+"QNum"+questionNumber+".wav")):
            os.remove("app/static/music/Test"+test+"QNum"+questionNumber+".wav")
        for question in questions[int(questionNumber):-1]:
            print(question.path.split("?")[0])
            if(question.path!="empty"):
                os.rename("app"+question.path.split("?")[0],"app/static/music/Test"+test+"QNum"+str(int(questionNumber))+".wav")
                if(os.path.isfile("/static/music/Test"+test+"QNum"+str(int(questionNumber)-1)+".wav")):
                    randomNumber = randint(0, 10000000000)
                    pathtoPage = "/static/music/Test"+test+"QNum"+str(int(questionNumber)-1)+".wav"+"?noCache="+str(randomNumber)
                    print("PRINT3")
                    question = Question(id=eachQuestion.id, body =questionForm.name.data,path=pathtoPage,test_id=test)
                    db.session.merge(question)
                else: 
                    print("PRINT4")
                    question = Question(id=eachQuestion.id, body =questionForm.name.data,path="empty",test_id=test)
                    db.session.merge(question)
        db.session.delete(eachQuestion)
        db.session.commit()
        return redirect(url_for('test', unitpage=unit.name, test=test, questionNumber=questionNumber))

    prefix = "app/"
    path = "/static/music/Test"+test+"QNum"+questionNumber+".wav"
    randomNumber = randint(0, 10000000000)
    pathtoPage = "/static/music/Test"+test+"QNum"+questionNumber+".wav"+"?noCache="+str(randomNumber)
    if request.method == "POST" or questionForm.validate_on_submit():
        if 'audio_data' in request.files:
            print("posted")
            f = request.files['audio_data']
            with open((prefix+path), 'wb') as audio:
                f.save(audio)
            print("File was successfully uploaded")
        if questionForm.validate_on_submit():
            if(eachQuestion=="" or eachQuestion==None):
                if(os.path.isfile(prefix+path)):
                    print("PRINT1")
                    question = Question( body =questionForm.name.data,path=pathtoPage,test_id=test)
                else: 
                    print("PRINT2")
                    question = Question( body = questionForm.name.data,path="empty",test_id=test)
            else:
                if(os.path.isfile(prefix+path)):
                    print("PRINT3")
                    question = Question(id=eachQuestion.id, body =questionForm.name.data,path=pathtoPage,test_id=test)
                else: 
                    print("PRINT4")
                    question = Question(id=eachQuestion.id, body = questionForm.name.data,path="empty",test_id=test)
            db.session.merge(question)
            db.session.commit()
            return redirect(url_for('test', unitpage = unit.name, test= test,questionNumber=int(questionNumber)+1))
    print(questions)
    return render_template('test.html', title="Edit task", unit=unit,deleteForm=deleteForm, form=questionForm, renameForm=renameForm, question=eachQuestion, questionNumber= questionNumber, 
    numOfQuestions= len(questions)-1, test = test, t = t, units = units,path=pathtoPage)

@app.route("/unitManager/<unitpage>/<test>/delete", methods=['GET', 'POST'])
def deleteTest(unitpage, test):
    unit = Unit.query.filter_by(name=unitpage).first()
    test = Test.query.filter_by(id=test).first()

    db.session.delete(test)
    db.session.commit()

    return redirect(url_for('unitpage', unitpage = unit.name))

@app.route("/unitManager/<unitpage>/delete", methods=['GET', 'POST'])
def deleteUnit(unitpage):
    if(current_user.isTeacher):
        unit = Unit.query.filter_by(name=unitpage).first()
        db.session.delete(unit)
        db.session.commit()
        studnetsEntrolled = User.query.filter_by(unit_id=unitpage).all()
        for eachStudent in studnetsEntrolled:
            eachStudent.unit_id = None
        else:
            internal_error(500)

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

from app.token import generate_confirmation_token, confirm_token
from app.email import send_email

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(id=form.studentNumber.data, email=form.email.data, firstName= form.firstName.data, LastName = form.lastName.data, confirmed=False)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        token = generate_confirmation_token(user.email)
        confirm_url = url_for('confirm_email', token=token, _external=True)
        html = render_template('email/activate.html', confirm_url=confirm_url)
        subject = "Please confirm your email"
        send_email(user.email, subject, html)
        flash('A confirmation email has been sent via email.', 'success')
        return redirect(url_for('unconfirmed'))
    return render_template('register.html', title='Register', form=form)

@app.route('/confirm/<token>')
def confirm_email(token):
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    try:
        email = confirm_token(token)
    except:
        flash('The confirmation link is invalid or has expired.', 'danger')
    user = User.query.filter_by(email=email).first_or_404()
    if user.confirmed:
        flash('Account already confirmed. Please login.', 'success')
    else:
        user.confirmed = True
        db.session.add(user)
        db.session.commit()
        flash('You have confirmed your account. Thanks!', 'success')
    return redirect(url_for('login'))

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


@app.route('/unconfirmed')
@login_required
def unconfirmed():
    if current_user.confirmed:
        return redirect('dashboard')
    flash('Please confirm your account!', 'warning')
    return render_template('unconfirmed.html')




@app.route('/resend')
@login_required
def resend_confirmation():
    token = generate_confirmation_token(current_user.email)
    confirm_url = url_for('confirm_email', token=token, _external=True)
    html = render_template('email/activate.html', confirm_url=confirm_url)
    subject = "Please confirm your email"
    send_email(current_user.email, subject, html)
    flash('A new confirmation email has been sent.', 'success')
    return redirect(url_for('unconfirmed'))
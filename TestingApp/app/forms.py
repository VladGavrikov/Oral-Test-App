from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, TextAreaField
from flask_wtf.file import FileField, FileRequired
from wtforms.validators import ValidationError, DataRequired,InputRequired, Email, EqualTo, NumberRange, Regexp,Length
from app.models import User
from wtforms.fields.html5 import EmailField
from wtforms import Form
from wtforms.fields.html5 import DateField, TimeField, DateTimeField

class LoginForm(FlaskForm):
    # email = EmailField('Email', validators=[DataRequired(), Email()])
    email = StringField('Email', validators=[DataRequired(), Email()]) #make it this
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    studentNumber = IntegerField('Student Number', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    firstName = StringField('First Name', validators=[DataRequired()])
    lastName = StringField('Last Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_studentNumber(self, studentNumber):
        user = User.query.filter_by(id=studentNumber.data).first()
        if user is not None:
            raise ValidationError('Please use a different student number.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class CreateUnitForm(FlaskForm):
    name = StringField('Unit Code', validators=[Regexp(r'^[\w.]+$', message="Invalid Characters."),Length(min=- 1, max=20), DataRequired()])
    description = StringField('Unit Name', validators=[DataRequired()])
    mark1Criteria = StringField('Marking criteria 1', validators=[DataRequired()])
    mark2Criteria = StringField('Marking criteria 2', validators=[DataRequired()])
    mark3Criteria = StringField('Marking criteria 3', validators=[DataRequired()])
    mark4Criteria = StringField('Marking criteria 4', validators=[DataRequired()])
    submit = SubmitField('Create Unit')

class CreateTestForm(FlaskForm):
    name = StringField('Task Name', validators=[DataRequired()])
    due_date = DateField('Date due', validators=[InputRequired()])
    due_time = TimeField('Time due', validators=[InputRequired()])
    submit = SubmitField('Add Test')

class CreateQuestionForm(FlaskForm):
    #name = TextAreaField('Question', validators=[DataRequired()])
    name = TextAreaField('Question', validators=[DataRequired()])
    submit = SubmitField('Save and add a new question')

class CreateAnswerForm(FlaskForm):
    audio = FileField(validators=[FileRequired()])
    submit = SubmitField('Save answer')

class CreateFeedbackForm(FlaskForm):
    body = StringField('Feedback')
    #body = StringField('Feedback', validators=[DataRequired()])
    submit = SubmitField('Save feedback')

class StartTest(FlaskForm):
    submit = SubmitField('Start Test')

class ReleaseFeedbackForm(FlaskForm):
    submit = SubmitField('Release Feedback')

class TestEvaluationForm(FlaskForm):
    mark1 = IntegerField('Accuracy', validators=[InputRequired(),NumberRange(min=0,max=25)])
    mark2 = IntegerField('Fluency', validators=[InputRequired(),NumberRange(min=0,max=25)])
    mark3 = IntegerField('Grammar', validators=[InputRequired(),NumberRange(min=0,max=25)])
    mark4 = IntegerField('Vocabulary', validators=[InputRequired(),NumberRange(min=0,max=25)])
    submit = SubmitField('Finish Marking')

class RenameTestForm(FlaskForm):
    newTestName = StringField('New Task Name', validators=[DataRequired()])
    submitRename = SubmitField('Save')

class DeleteQuestionForm(FlaskForm):
    submitDelete = SubmitField('Delete')
    
class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Request Password Reset')

class ResetDatabaseForm(FlaskForm):
    passwordResetter = StringField('Reset database password', validators=[DataRequired()])
    submit = SubmitField('Reset database')

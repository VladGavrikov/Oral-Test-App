from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField
from flask_wtf.file import FileField, FileRequired
from wtforms.fields.html5 import DateField  
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import User
from wtforms.fields.html5 import EmailField

class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
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
        print("++++++++++++++++++I AM HERE++++++++++++++++++")
        user = User.query.filter_by(id=studentNumber.data).first()
        if user is not None:
            raise ValidationError('Please use a different student number.')

    def validate_email(self, email):
        print("++++++++++++++++++I AM HERE2++++++++++++++++++")
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class CreateUnitForm(FlaskForm):
    name = StringField('Unit Name', validators=[DataRequired()])
    description = StringField('Unit Description', validators=[DataRequired()])
    submit = SubmitField('Create Unit')

class CreateTestForm(FlaskForm):
    name = StringField('Test Name', validators=[DataRequired()])
    deadline = DateField('Deadline', format='%Y-%m-%d')
    submit = SubmitField('Add Test')

class CreateQuestionForm(FlaskForm):
    name = StringField('Question', validators=[DataRequired()])
    submit = SubmitField('Add Question')

class CreateAnswerForm(FlaskForm):
    audio = FileField(validators=[FileRequired()])
    submit = SubmitField('Submit answer')

class CreateFeedbackForm(FlaskForm):
    body = StringField('Feedback', validators=[DataRequired()])
    submit = SubmitField('Submit feedback')

class StartTest(FlaskForm):
    submit = SubmitField('Start Test')

class ReleaseFeedbackForm(FlaskForm):
    submit = SubmitField('Release Feedback')

class TestEvaluationForm(FlaskForm):
    mark1 = StringField('Accuracy', validators=[DataRequired()])
    mark2 = StringField('Fluency', validators=[DataRequired()])
    mark3 = StringField('Grammar', validators=[DataRequired()])
    mark4 = StringField('Vocabulary', validators=[DataRequired()])
    submit = SubmitField('Finish Marking')
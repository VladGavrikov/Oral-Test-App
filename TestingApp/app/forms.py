from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import User

class LoginForm(FlaskForm):
    username = StringField('Student Number', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class CreateUnitForm(FlaskForm):
    name = StringField('Unit Name', validators=[DataRequired()])
    description = StringField('Unit Description', validators=[DataRequired()])
    submit = SubmitField('Create Unit')

class CreateTestForm(FlaskForm):
    name = StringField('Test Name', validators=[DataRequired()])
    submit = SubmitField('Add Test')

class CreateQuestionForm(FlaskForm):
    name = StringField('Question', validators=[DataRequired()])
    submit = SubmitField('Add Question')

class CreateAnswerForm(FlaskForm):
    body = StringField('Answer', validators=[DataRequired()])
    submit = SubmitField('Submit answer')
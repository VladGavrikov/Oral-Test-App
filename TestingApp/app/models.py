from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app import db
from app import login
from time import time
import jwt
from app import app

from flask_login import UserMixin


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True,unique=True)
    unit_id = db.Column(db.String(20), db.ForeignKey('unit.name'))
    email = db.Column(db.String(120), index=True, unique=True)
    firstName = db.Column(db.String(64))
    LastName = db.Column(db.String(64))
    password_hash = db.Column(db.String(128))
    isTeacher = db.Column(db.Boolean, default=False)
    answer = db.relationship('Answer', backref='user', lazy='dynamic')
    confirmed = db.Column(db.Boolean, default=False)
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.id)
    

    def get_reset_password_token(self, expires_in=600):
         return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id) 


class Unit(db.Model):
    name = db.Column(db.String(20), primary_key=True)
    description = db.Column(db.String(50))
    mark1Criteria = db.Column(db.String(50))
    mark2Criteria = db.Column(db.String(50))
    mark3Criteria = db.Column(db.String(50))
    mark4Criteria = db.Column(db.String(50))
    tests = db.relationship('Test', backref='author', lazy='dynamic')

    def __repr__(self):
        return '<Unit {}>'.format(self.description)

class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    due_date = db.Column(db.Date)
    due_time = db.Column(db.Time)
    feedbackReleased = db.Column(db.Boolean, default=False)
    isFinalized = db.Column(db.Boolean, default=False)
    unit_id = db.Column(db.String(20), db.ForeignKey('unit.name'))
    questions = db.relationship('Question', backref='author', lazy='dynamic')
    
    def __repr__(self):
        return '<Test {}>'.format(self.body)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    path = db.Column(db.String(140))
    test_id = db.Column(db.Integer, db.ForeignKey('test.id'))
    answer = db.relationship('Answer', backref='answer', lazy='dynamic')

    def __repr__(self):
        return '<Question {}>'.format(self.body)

class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    

    def __repr__(self):
        return '<Answer {}>'.format(self.body)

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    path = db.Column(db.String(140))
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))
    answer_id = db.Column(db.Integer, db.ForeignKey('answer.id'))

    def __repr__(self):
        return '<Feedback {}>'.format(self.body)

class TestMark(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    test_id = db.Column(db.Integer, db.ForeignKey('test.id'))
    unit_id = db.Column(db.String(20), db.ForeignKey('unit.name'))
    #Will be separated in 4 mark rubrics
    mark = db.Column(db.Integer, default=-1)
    testWasStarted = db.Column(db.Boolean, default=False)
    feedbackReleased = db.Column(db.Boolean, default=False)
    hasBeenMarked = db.Column(db.Boolean, default=False)
    due_date = db.Column(db.Date)
    due_time = db.Column(db.Time)
    mark1 = db.Column(db.Integer)
    mark2 = db.Column(db.Integer)
    mark3 = db.Column(db.Integer)
    mark4 = db.Column(db.Integer)

    users = db.relationship(User)
    tests = db.relationship(Test)
    def __repr__(self):
        return '<TestMark {}>'.format(self.id)




from time import time
import jwt
from app import app

from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app import db
from app import login

from flask_login import UserMixin


@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
<<<<<<< Updated upstream
=======
    email_confirm = db.Column(db.Boolean,default = False)
    firstName = db.Column(db.String(64))
    LastName = db.Column(db.String(64))
>>>>>>> Stashed changes
    password_hash = db.Column(db.String(128))
<<<<<<< Updated upstream
    unit = db.relationship('Unit', backref='author', lazy='dynamic')

=======
    isTeacher = db.Column(db.Boolean, default=False)
    units_enrolled = db.Column(db.String(20), db.ForeignKey('unit.name'))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
>>>>>>> Stashed changes
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)

<<<<<<< Updated upstream

=======
    def get_reset_password_token(self, expires_in=600):
         return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8') 
    def get_confirm_email_token(self, expires_in = 1000):
        return jwt.encode(
            {'confirm_email': self.id,'exp': time() +expires_in},
            app.config['SECRET_KEY'], algorithm = 'HS256').decode('utf-8')

                

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id) 
    @staticmethod    
    def confirm_email_token(token):
        try:
            id = jwt.decode(token,app.config['SECRET_KEY'],
                            algorithms = ['HS256'])['confirm_email']
        except:
            return
        return User.query.get(id)    

>>>>>>> Stashed changes

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)

class Unit(db.Model):
<<<<<<< Updated upstream
=======
    name = db.Column(db.String(20), primary_key=True)
    description = db.Column(db.String(50))
    tests = db.relationship('Test', backref='author', lazy='dynamic')
    students = db.relationship('Enrolled Students', backref = 'students', lazy = 'dynamic')
    def __repr__(self):
        return '<Unit {}>'.format(self.body)

class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    isFinalized = db.Column(db.Boolean, default=False)
    unit_id = db.Column(db.String(20), db.ForeignKey('unit.name'))
    questions = db.relationship('Question', backref='author', lazy='dynamic')
    
    def __repr__(self):
        return '<Test {}>'.format(self.body)

class TestCompleted(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    test_id = db.Column(db.Integer, db.ForeignKey('test.id'))
    score = db.Column(db.Integer)


class Question(db.Model):
>>>>>>> Stashed changes
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    description = db.Column(db.String(50))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

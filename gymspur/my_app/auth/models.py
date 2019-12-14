from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import FieldList, FormField, TextField, PasswordField, TextAreaField, SubmitField, IntegerField
from wtforms.validators import InputRequired, EqualTo, DataRequired
from my_app import db
from datetime import date

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    pwdhash = db.Column(db.String())
    days = db.relationship('Day', backref='user', lazy='dynamic')
    exercises = db.relationship('Exercise', backref='user', lazy='dynamic')

    def __init__(self, username, password):
        self.username = username
        self.pwdhash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.pwdhash, password)
    
    @property
    def is_authenticated(self):
        return True
    
    @property 
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

class Day(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    day_name = db.Column(db.String(120), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    exercises = db.relationship('Exercise', backref='day', lazy='dynamic')

class Exercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exr_mg = db.Column(db.String(120))
    exr_name = db.Column(db.String(120), nullable=False)
    exr_reps = db.Column(db.Integer)
    exr_sets = db.Column(db.Integer)
    exr_val = db.Column(db.Integer)
    day_id = db.Column(db.Integer, db.ForeignKey('day.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    weekly_values = db.relationship('Weekly_Value', backref='exercise', lazy='dynamic')

class Weekly_Value(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Integer)
    date = db.Column(db.Date)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercise.id'))

    def __init__(self, value, exercise_id):
        self.value = value
        self.exercise_id = exercise_id
        self.date = date.today()

class RegistrationForm(FlaskForm):
    username = TextField('Username', [InputRequired()])
    password = PasswordField(
        'Password', [
            InputRequired(), EqualTo('confirm', message='Passwords must match')
        ]
    )
    confirm = PasswordField('Confirm Password', [InputRequired()])

class LoginForm(FlaskForm):
    username = TextField('Username', [InputRequired()])
    password = PasswordField('Password', [InputRequired()])

class DayForm(FlaskForm):
    day = TextAreaField('Add a new day', validators=[DataRequired()])
    submit = SubmitField('Submit')

class ExerciseForm(FlaskForm):
    exercise = TextAreaField('Add a new exercise', validators=[DataRequired()])
    muscle_group = TextAreaField('Muscle Group', validators=[DataRequired()])
    reps = IntegerField('Reps')
    sets = IntegerField('Sets')
    value = IntegerField('Value')
    submit = SubmitField('Submit')

class ExercisesForm(FlaskForm):
    title = TextAreaField('title')
    exercises = FieldList(FormField(ExerciseForm))

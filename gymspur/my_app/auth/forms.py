from flask_wtf import FlaskForm
from wtforms import FieldList, FormField, TextField, PasswordField, TextAreaField, SubmitField, IntegerField
from wtforms.validators import InputRequired, EqualTo, DataRequired

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
    day = TextField('Add a new day', validators=[DataRequired()])
    submit = SubmitField('Submit')

class ExerciseForm(FlaskForm):
    exercise = TextAreaField('Add a new exercise', validators=[DataRequired()])
    muscle_group = TextField('Muscle Group', validators=[DataRequired()])
    reps = IntegerField('Reps', default=0, validators=[DataRequired()])
    sets = IntegerField('Sets', default=0, validators=[DataRequired()]) 
    value = IntegerField('Value', default=0, validators=[DataRequired()])
    submit = SubmitField('Submit')

class ExerciseNameForm(FlaskForm):
    exercise = TextAreaField('Add a new exercise', validators=[DataRequired()])
    submit = SubmitField('Submit')

class EditProfileForm(FlaskForm):
    username = TextField('Username', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')
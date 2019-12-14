from flask import request, render_template, flash, redirect, url_for, \
    session, Blueprint, g
from flask_login import current_user, login_user, logout_user, login_required
from flask_dance.contrib.facebook import make_facebook_blueprint, facebook
from my_app import app, db, login_manager
from my_app.auth.models import User, Day, Exercise, Weekly_Value
from my_app.auth.forms import RegistrationForm, LoginForm, DayForm, \
     ExerciseForm, ExerciseNameForm
import matplotlib.pyplot as plt
import matplotlib as mpl

auth = Blueprint('auth', __name__)
facebook_blueprint = make_facebook_blueprint(scope='email', redirect_to='auth.facebook_login')

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@auth.before_request
def get_current_user():
    g.user = current_user

@auth.route('/routine', methods=['GET', 'POST'])
@login_required
def routine():
    e_form = ExerciseForm(csrf_enabled=False)
    en_form = ExerciseNameForm(csrf_enabled=False)
    change_exercise_form = ExerciseForm(csrf_enabled=False)
    form = DayForm(csrf_enabled=False)
    if form.validate_on_submit():
        day = Day(day_name=form.day.data, user=current_user)
        db.session.add(day)
        db.session.commit()
        flash("%s added!" % day.day_name)
        return redirect(url_for('auth.routine'))
    days = current_user.days
    muscle_groups = {}
    for day in days:
        muscle_groups[day.id] = []
        for exercise in day.exercises:
            if exercise.exr_mg not in muscle_groups[day.id]:
                muscle_groups[day.id].append(exercise.exr_mg)
    return render_template('routine/routine.html', title='routine', form=form, e_form=e_form,\
         days=days, en_form=en_form, change_exercise_form=change_exercise_form, muscle_groups=muscle_groups)

@auth.route('/routine/delete/<int:day_id>', methods=['GET', 'DELETE'])
@login_required
def delete_day(day_id):
    Day.query.filter_by(id=day_id).delete()
    ex = Exercise.query.filter_by(day_id=day_id).all()
    for exer in ex:
        Weekly_Value.query.filter_by(exercise_id=exer.id).delete()
    Exercise.query.filter_by(day_id=day_id).delete()
    db.session.commit()
    return redirect(url_for('auth.routine'))

@auth.route('/routine/rename/<int:day_id>', methods=['GET', 'POST'])
@login_required
def rename_day(day_id):
    form = DayForm(csrf_enabled=False)
    if form.validate_on_submit():
        og_day = Day.query.filter_by(id=day_id).first().day_name
        Day.query.filter_by(id=day_id).first().day_name = form.day.data
        new_day = Day.query.filter_by(id=day_id).first().day_name
        db.session.commit()
        flash(og_day + " changed to: " + new_day)
        return redirect(url_for('auth.routine'))
    return redirect(url_for('auth.routine'))

@auth.route('/routine/add-exercise/<int:day_id>', methods=['GET', 'POST'])
@login_required
def add_exercise(day_id):
    e_form = ExerciseForm(csrf_enabled=False)
    if e_form.validate_on_submit():
        exercise = Exercise(exr_name=e_form.exercise.data,
        exr_mg=e_form.muscle_group.data.upper(), exr_sets=e_form.sets.data, 
        exr_reps=e_form.reps.data, exr_val=e_form.value.data, day_id=day_id, user_id=current_user.id)
        db.session.add(exercise)
        db.session.commit()

        init_val = Weekly_Value(exercise.exr_val, exercise.id)
        db.session.add(init_val)
        db.session.commit()
        flash("%s added!" % exercise.exr_name)
        return redirect(url_for('auth.routine'))
    else:
        flash("Reps, Sets and Weight only take numerical values! Try again.", "error")
        return redirect(url_for('auth.routine'))
    return render_template('routine/routine.html', title='routine', e_form=e_form)

@auth.route('/routine/delete-exercise/<int:exercise_id>', methods=['GET', 'DELETE'])
@login_required
def delete_exercise(exercise_id):
    Exercise.query.filter_by(id=exercise_id).delete()
    Weekly_Value.query.filter_by(exercise_id=exercise_id).delete()
    db.session.commit()
    return redirect(url_for('auth.routine'))

@auth.route('/routine/rename-exercise/<int:exercise_id>', methods=['GET', 'POST'])
@login_required
def change_exercise(exercise_id):
    en_form = ExerciseNameForm(csrf_enabled=False)
    if en_form.validate_on_submit():
        og_exercise = Exercise.query.filter_by(id=exercise_id).first().exr_name
        Exercise.query.filter_by(id=exercise_id).first().exr_name = en_form.exercise.data
        new_exercise = Exercise.query.filter_by(id=exercise_id).first().exr_name
        db.session.commit()
        flash(og_exercise + " changed to: " + new_exercise)
        return redirect(url_for('auth.routine'))
    return redirect(url_for('auth.routine'))

@auth.route('/routine/rename-mg/<int:exercise_id>', methods=['POST'])
@login_required
def change_mg(exercise_id):
    change_exercise_form = ExerciseForm(csrf_enabled=False)
    exercise = Exercise.query.filter_by(id=exercise_id).first()
    if change_exercise_form.validate_on_submit():
        exercise.exr_mg = change_exercise_form.muscle_group.data
        exercise.exr_name = change_exercise_form.exercise.data
        exercise.exr_sets = change_exercise_form.sets.data
        exercise.exr_reps = change_exercise_form.reps.data
        if exercise.exr_val != change_exercise_form.value.data:
            #update weight value, add to values and add to database
            exercise.exr_val = change_exercise_form.value.data
            new_value = Weekly_Value(exercise.exr_val, exercise.id)
            db.session.add(new_value)
        db.session.commit()
        return redirect(url_for('auth.routine'))
    return redirect(url_for('auth.routine'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if session.get('username'):
        flash("You are already logged in.", 'info')
        return redirect(url_for('auth.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        username = request.form.get('username')
        password = request.form.get('password')
        existing_username = User.query.filter_by(username=username).first()
        if existing_username:
            flash(
                'This username has been already taken. Try another one.',
                'warning'
            )
            return render_template('auth/register.html', form=form)
        user = User(username, password)
        db.session.add(user)
        db.session.commit()
        flash('You are now registered. Please login.', 'success')
        return redirect(url_for('auth.login'))
    if form.errors:
        flash(form.errors, 'danger')
    return render_template('auth/register.html', form=form)

@auth.route('/')
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash('You are already logged in.', 'info')
        return redirect(url_for('auth.routine'))
    form = LoginForm()
    if form.validate_on_submit():
        username = request.form.get('username')
        password = request.form.get('password')
        existing_user = User.query.filter_by(username=username).first()
        if not (existing_user and existing_user.check_password(password)):
            flash('Invalid username or password. Please try again.', 'danger')
            return render_template('auth/login.html', form=form)
        login_user(existing_user)
        flash('You have successfully logged in.', 'success')
        return redirect(url_for('auth.routine'))
    if form.errors:
        flash(form.errors, 'danger')
    return render_template('auth/login.html', form=form)

@auth.route("/facebook-login")
def facebook_login():
    if not facebook.authorized:
        return redirect(url_for("facebook.login"))
    resp = facebook.get("/me?fields=name,email")
    user = User.query.filter_by(username=resp.json()["email"]).first()
    if not user:
        user = User(resp.json()["email"], '')
        db.session.add(user)
        db.session.commit()
    login_user(user)
    flash("Login in as name=%s using Facebook login" % (resp.json()['name']), 'success')
    return redirect(request.args.get('next', url_for('auth.routine')))

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

#TRACK----------------------------------------------
@auth.route('/track', methods=['GET'])
@login_required
def track():
    exercises = current_user.exercises
    return render_template('track/track.html', exercises=exercises, Exercise=Exercise)

@auth.route('/trackexercise')
@login_required
def trackexercise():
    chart_id = request.args['chart_id']
    exercises = current_user.exercises
    return render_template('track/track.html', exercises=exercises, chart_id=chart_id, Exercise=Exercise)

@auth.route('/loadchart', methods=['POST'])
@login_required
def loadchart():
    COLOR = 'white'
    PLOT_COLOR = "#66fcf1"
    FILL_COLOR = "#45a29e"
    STRENGTH_GAIN = True


    mpl.rcParams['text.color'] = COLOR
    mpl.rcParams['axes.labelcolor'] = COLOR
    mpl.rcParams['xtick.color'] = COLOR
    mpl.rcParams['ytick.color'] = COLOR

    _id = request.form.get('myList')
    exercise = Exercise.query.filter_by(id=_id).first()

    dates=[]
    values=[]
    for v in exercise.weekly_values:
        dates.append(v.date)
        values.append(v.value)   
    if len(values) > 1:
        if values[-1] < values[-2]:
            STRENGTH_GAIN = False
            PLOT_COLOR = "#EA4D2B"
            FILL_COLOR = "#BF3011"
    else:
        STRENGTH_GAIN = None

    fig, ax = plt.subplots()
    ax.plot(dates, values, linewidth=5, color=PLOT_COLOR)
    ax.set_facecolor("#1f2833")
    ax.fill_between(dates,values, color=FILL_COLOR)
    str_xticks = [dates[0].strftime("%d %b %Y"), dates[-1].strftime("%d %b %Y"),]
    plt.xticks([dates[0], dates[-1]], str_xticks)
    plt.yticks([value for value in values])
    fig.patch.set_alpha(0)
    plt.savefig("my_app/static/images/progress-"+str(exercise.id)+".png",
    facecolour=fig.get_facecolor(), edgecolor="none")
    chart_id = _id
    
    return redirect(url_for('auth.trackexercise', chart_id=chart_id, Exercise=Exercise))

#USER-----------------------------------------------
@auth.route('/account')
@login_required
def account():
     return render_template('user/account.html')

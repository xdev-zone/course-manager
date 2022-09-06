from datetime import datetime
from urllib import response
from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.forms import EditCourseForm, LoginForm, RegistrationForm, EditProfileForm, \
    EmptyForm, ResetPasswordRequestForm, ResetPasswordForm, EditCourseForm
from app.models import User, Course
from app.email import send_password_reset_email
from sqlalchemy import func


@app.route("/admin-restricted")
@login_required
def admin_resource():
    if current_user.role == "admin":
        flash('hey admin!')
        return redirect(url_for('index'))
    else:
        flash('You dont are an admin!')
        return redirect(url_for('index'))

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    courses = Course.query.filter_by(visible=1).order_by(Course.date.desc()).paginate(
        page, app.config['ITEMS_PER_PAGE'], False)
    next_url = url_for('courses', page=courses.next_num) \
        if courses.has_next else None
    prev_url = url_for('courses', page=courses.prev_num) \
        if courses.has_prev else None
    form = EmptyForm()
    return render_template('index.html', title='Welcome to Course-Manager', courses=courses.items,
                           next_url=next_url, prev_url=prev_url, form=form)


@app.route('/courses')
@login_required
def courses():
    page = request.args.get('page', 1, type=int)
    courses = Course.query.filter_by(visible=1).order_by(Course.date.desc()).paginate(
    page, app.config['ITEMS_PER_PAGE'], False)
    next_url = url_for('courses', page=courses.next_num) \
        if courses.has_next else None
    prev_url = url_for('courses', page=courses.prev_num) \
        if courses.has_prev else None
    form = EmptyForm()
    return render_template('index.html', title='Our Courses', courses=courses.items,
                           next_url=next_url, prev_url=prev_url, form=form)

@app.route('/manage_courses')
@login_required
def manage_courses():
    page = request.args.get('page', 1, type=int)
    courses = Course.query.order_by(Course.date.desc()).paginate(
    page, app.config['ITEMS_PER_PAGE'], False)
    next_url = url_for('courses', page=courses.next_num) \
        if courses.has_next else None
    prev_url = url_for('courses', page=courses.prev_num) \
        if courses.has_prev else None
    form = EmptyForm()
    return render_template('index.html', title='Manage Courses', courses=courses.items,
                           next_url=next_url, prev_url=prev_url, form=form)



@app.route('/registrated_courses')
@login_required
def registrated_courses():
    page = request.args.get('page', 1, type=int)
    courses = current_user.registrated_courses().order_by(Course.date.desc()).paginate(
    page, app.config['ITEMS_PER_PAGE'], False)
    next_url = url_for('registrated_courses', page=courses.next_num) \
        if courses.has_next else None
    prev_url = url_for('registrated_courses', page=courses.prev_num) \
        if courses.has_prev else None

    form = EmptyForm()
    return render_template('index.html', title='See your Registrations', courses=courses.items, 
                            next_url=next_url, prev_url=prev_url, form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/instructed_courses')
@login_required
def instructed_courses():
    page = request.args.get('page', 1, type=int)
    courses = Course.query.filter_by(instructor_id=current_user.id).order_by(Course.date.desc()).paginate(
    page, app.config['ITEMS_PER_PAGE'], False)
    next_url = url_for('instructed_courses', page=courses.next_num) \
        if courses.has_next else None
    prev_url = url_for('instructed_courses', page=courses.prev_num) \
        if courses.has_prev else None
    form = EmptyForm()
    return render_template('index.html', title='Find your Courses', courses=courses.items, 
                            next_url=next_url, prev_url=prev_url, form=form)



@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)


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


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    courses = user.courses.order_by(Course.date.desc()).paginate(
        page, app.config['ITEMS_PER_PAGE'], False)
    next_url = url_for('user', username=user.username, page=courses.next_num) \
        if courses.has_next else None
    prev_url = url_for('user', username=user.username, page=courses.prev_num) \
        if courses.has_prev else None
    form = EmptyForm()
    return render_template('user.html', user=user, courses=courses.items,
                           next_url=next_url, prev_url=prev_url, form=form)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        current_user.name = form.name.data
        current_user.address = form.address.data
        current_user.postalcode = form.postalcode.data
        current_user.city = form.city.data
        current_user.role = form.role.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
        form.name.data = current_user.name
        form.address.data = current_user.address
        form.postalcode.data = current_user.postalcode
        form.city.data = current_user.city
        form.role.data = current_user.role
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)

@app.route('/edit_course/<id>', methods=['GET', 'POST'])
@login_required
def edit_course(id):
    course = Course.query.filter_by(id=id).first_or_404()
    if current_user.role != "admin" and course.instructor_id != current_user.id:
        flash("You don't have permission to access this resource!")
        return redirect(url_for('index'))

    course = Course.query.filter_by(id=id).first_or_404()
    form = EditCourseForm(course.id)
    form.instructor_id.choices = [(i.id, i.username) for i in User.query.order_by('username')]

    if form.validate_on_submit():
        course.id = form.id.data
        course.title = form.title.data
        course.description = form.description.data
        course.seats = form.seats.data
        course.date = form.date.data
        course.instructor_id = form.instructor_id.data
        course.visible = form.visible.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('manage_courses'))
    elif request.method == 'GET':
        form.id.data = course.id
        form.title.data = course.title
        form.description.data = course.description
        form.seats.data = course.seats
        form.date.data = course.date
        form.instructor_id.data = course.instructor_id
        form.visible.data = course.visible
    return render_template('edit_course.html', title='Edit Course',
                           form=form)

@app.route('/new_course', methods=['GET', 'POST'])
@login_required
def new_course():
    if current_user.role != "admin":
        flash("You don't have permission to access this resource!")
        return redirect(url_for('index'))
    if Course.query.first():
        course_id = Course.query.order_by(Course.id.desc()).first().id + 1
    else:
        course_id = 1
    form = EditCourseForm(course_id)
    form.instructor_id.choices = [(i.id, i.username) for i in User.query.order_by('username')]

    if form.validate_on_submit():
        course = Course(id=course_id)
        course.title = form.title.data
        course.description = form.description.data
        course.seats = form.seats.data
        course.date = form.date.data
        course.instructor_id = form.instructor_id.data
        course.visible = form.visible.data
        db.session.add(course)
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('manage_courses'))
    elif request.method == 'GET':
        form.id.data = course_id
    return render_template('edit_course.html', title='New Course',
                           form=form)


@app.route('/register/<course_id>', methods=['POST'])
@login_required
def register_course(course_id):
    form = EmptyForm()
    if form.validate_on_submit():
        course = Course.query.filter_by(id=course_id).first()
        course.register(current_user)
        db.session.commit()
        flash('You have successfully registered for course {}!'.format(course.title))
        return redirect(request.referrer)
    else:
        return redirect(url_for('index'))

@app.route('/unregister/<course_id>', methods=['POST'])
@login_required
def unregister_course(course_id):
    form = EmptyForm()
    if form.validate_on_submit():
        course = Course.query.filter_by(id=course_id).first()
        course.unregister(current_user)
        db.session.commit()
        flash('You have successfully deregistered for course {}!'.format(course.title))
        return redirect(request.referrer)
    else:
        return redirect(url_for('index'))

@app.route('/delete_course/<course_id>', methods=['POST'])
@login_required
def delete_course(course_id):
    form = EmptyForm()
    if form.validate_on_submit():
        course = Course.query.filter_by(id=course_id).first()
        db.session.delete(course)
        db.session.commit()
        flash('Course {} is now deleted!'.format(course.title))
        return redirect(request.referrer)
    else:
        return redirect(url_for('index'))


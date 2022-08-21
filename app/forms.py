from pydoc import visiblename
from flask_wtf import FlaskForm
from sqlalchemy import Integer
from wtforms import StringField, PasswordField, BooleanField, SubmitField, \
    TextAreaField, IntegerField, DateField, SelectField, DateTimeLocalField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, \
    Length, NumberRange
from wtforms.widgets import DateTimeInput
from app.models import User


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
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


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Request Password Reset')


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    name = StringField('Name', validators=[Length(min=0, max=128)])
    address = StringField('Address', validators=[Length(min=0, max=128)])
    postalcode = IntegerField('Postal code', validators=[NumberRange(1,99999)])
    city = StringField('City', validators=[Length(min=0, max=128)])
    role = StringField('Role')
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')

class EditCourseForm(FlaskForm):
    id = IntegerField('Id', render_kw={'readonly': True})
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Length(min=0, max=128)])
    instructor_id = SelectField('Instructor', coerce=int)
    seats = IntegerField('Seats', validators=[NumberRange(0,100)])
    date = DateTimeLocalField('Date', format='%Y-%m-%dT%H:%M')
    visible = BooleanField('Published')
    submit = SubmitField('Submit')

    def __init__(self, original_id, *args, **kwargs):
        super(EditCourseForm, self).__init__(*args, **kwargs)
        self.original_id = original_id


class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')
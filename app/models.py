from datetime import datetime
from dis import Instruction
from hashlib import md5
from pydoc import visiblename
from time import time
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from app import app, db, login


followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

attendees = db.Table(
    'attendees',
    db.Column('attendee_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('course_id', db.Integer, db.ForeignKey('course.id'))
)



class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    courses = db.relationship('Course', backref='instructor', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    name = db.Column(db.String(128))
    address = db.Column(db.String(128))
    postalcode = db.Column(db.Integer)
    city = db.Column(db.String(128))
    role = db.Column(db.String(128))

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def registrated_courses(self):
        self.course_attendees
        return self.course_attendees.order_by(Course.date.desc())

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64))
    description = db.Column(db.String(128))
    seats = db.Column(db.Integer)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    visible = db.Column(db.Integer)
    instructor_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    registrated = db.relationship(
        'User', secondary=attendees,
        primaryjoin=(attendees.c.course_id == id),
        secondaryjoin=(attendees.c.attendee_id == User.id),
        backref=db.backref('course_attendees', lazy='dynamic'), lazy='dynamic')

    def available_seats(self):
        return self.seats - self.registrated.count()
    
    def register(self, user):
        if not self.is_registered(user):
            self.registrated.append(user)

    def unregister(self, user):
        if self.is_registered(user):
            self.registrated.remove(user)

    def is_registered(self, user):
        return self.registrated.filter(
            attendees.c.course_id == self.id).filter(attendees.c.attendee_id == user.id).count() > 0

    def avatar(self, size):
        digest = md5(self.title.encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def to_dict(self):
        data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'seats': self.seats,
            'available_seats': self.available_seats(),
            'date': self.date,
            'visible': self.visible,
            'instructor_id': self.instructor_id,
        }
        return data

    def from_dict(self, data):
        for field in ['title', 'description', 'seats', 'date', 'visible', 'instructor_id']:
            if field in data:
                setattr(self, field, data[field])

    @staticmethod
    def to_collection():
        courses = Course.query.all()
        data = {'items': [item.to_dict() for item in courses]}
        return data
        
    def __repr__(self):
        return '<Course {}>'.format(self.id)
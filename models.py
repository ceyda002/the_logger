# this is for defining database tables
from extensions import db 
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime




#user table 
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True) #SQLAlchemy track the user
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    courses = db.relationship('Course', backref='owner', lazy=True)

def __repr__(self):
    return f"User('{self.username}', '{self.email}')"

# course table
class Course(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True) 
    coursename = db.Column(db.String(150), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='planned')
    createdat = db.Column(db.DateTime, default=datetime.utcnow)
    manual_hours = db.Column(db.Integer, default=0)
    total_hours = db.Column(db.Integer, nullable=False, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # links the course to a user 
    sess = db.relationship('Sess', backref='course', lazy=True, cascade="all, delete-orphan")
    tags = db.Column(db.String(200))
    def __repr__(self):
        return f'<Course {self.coursename} ({self.status}) {self.total_hours}h>'


    ##session logging
class Sess(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    date = db.Column(db.Date, default=datetime.utcnow)
    hours = db.Column(db.Integer, default=0)
    minutes = db.Column(db.Integer, default=0)
    notes = db.Column(db.Text)


    def __repr__(self):
        return f"<Session {self.course_id} {self.date}>"

        
class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text)
    file_path = db.Column(db.String(225))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    course = db.relationship('Course', backref=db.backref('notes', lazy=True))
    
def get_db():
    from app import db
    return db

from app import db,login_manager
from datetime import datetime
from flask_login import UserMixin
# need to dectorate the function bech extenstiion know to get the user by id
# the extension will expect user model to have certain attributes and methods iSauthanticated isactive isananmous getid all thos function provided by
# extention eli ta3tina class nehritiw meno hetha kol
# UserMixin
@login_manager.user_loader
def load_user(user_id):
    # this function well return the user  based on his id
    return User.query.get(int(user_id))


class User(db.Model,UserMixin):
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(20),unique=True,nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False,default='default.jpg')
    password = db.Column(db.String(60),nullable=False)
    workpost = db.Column(db.String(20))
    Registration_Date =db.Column(db.DateTime,nullable=False,default=datetime.utcnow)
    posts = db.relationship('Post',backref='author',lazy=True)
    course = db.relationship('Course',backref='doctor',lazy=True)
    # backref like adding new col to post model like we have post we can use this attribute to get the user
    # created this post
    def __repr__(self):
        return f"User('{self.username}','{self.email}','{self.workpost}','{self.image_file}','{self.Registration_Date}')"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100),nullable=False)
    date_posted = db.Column(db.DateTime,nullable=False,default=datetime.utcnow)
    content = db.Column(db.Text,nullable=False)
    # one to many relation one user can have many post but one post have unique user
    #specify the user posted the post
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False) # integer 5taer hia primary key ta3 user
    def __repr__(self):
        return f"Post('{self.title}','{self.date_posted}')"


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    intro =  db.Column(db.Text, nullable=False)
    image_file = db.Column(db.String(20), nullable=False)
    #video_file = db.Column(db.String(20))
    #pdf_file = db.Column(db.String(20))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Course('{self.title}','{self.intro}','{self.image_file}')"

class Chapters(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    intro = db.Column(db.Text, nullable=False)
    video_file = db.Column(db.String(20))
    pdf_file = db.Column(db.String(20))
    id_course = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"Chapter('{self.title}','{self.pdf_file}','{self.video_file}','{self.id_course}')"

class CoronaDailyUpdateds(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    confirmed = db.Column(db.Integer, nullable=False)
    recoverd = db.Column(db.Integer, nullable=False)
    deaths = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow,unique=True)








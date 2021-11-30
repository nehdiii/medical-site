from flask_wtf import FlaskForm
from flask_wtf.file import FileField,FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField,SelectField,TextAreaField,IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo,ValidationError
from app.models import User


class RegistrationForm(FlaskForm):
    username = StringField('Nom d\'Utilisateur',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Mot de Passe', validators=[DataRequired()])
    confirm_password = PasswordField('Confirmer le Mot De Passe',
                                     validators=[DataRequired(), EqualTo('password')])
    workpost = SelectField('Poste D\'Emploi',choices=[('dr','doctor'),('np','new personel')])
    submit = SubmitField('Inscrivez-Vous')

    # costum validation for register form
    # it gets checked when we try to validate the form and return the visual feed back of error messages
    def validate_username(self,username):
        user = User.query.filter_by(username=username.data).first()
        # itha fama user fi data base and esm heka traja3li name te3ko sinon traja3 none
        # if user exist we will therow our validation error
        if user:
            raise ValidationError('That username is taken. Please choose a diffrent one.')
    def validate_email(self,email):
        user = User.query.filter_by(email=email.data).first()
        # itha fama user fi data base and esm heka traja3li name te3ko sinon traja3 none
        # if user exist we will therow our validation error
        if user:
            raise ValidationError('That email is taken. Please choose a diffrent one.')

class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Mot De Passe', validators=[DataRequired()])
    remember = BooleanField('Se Souvenir De Moi')
    submit = SubmitField('Se Connecter')

class UpdateAccountForm(FlaskForm):
    username = StringField('Nom d\'Utilisateur',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])

    picture = FileField('Mettre à jour la photo de profil',validators=[FileAllowed(['jpg','png'])])
    submit = SubmitField('Update')

    # costum validation for register form
    # it gets checked when we try to validate the form and return the visual feed back of error messages
    def validate_username(self,username):
        # we will test if acurrent username is diffrent leli da5lo user fi updates
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            # itha fama user fi data base and esm heka traja3li name te3ko sinon traja3 none
            # if user exist we will therow our validation error
            if user:
                raise ValidationError('That username is taken. Please choose a diffrent one.')
    def validate_email(self,email):
        if email.data != current_user.email :
            user = User.query.filter_by(email=email.data).first()
            # itha fama user fi data base and esm heka traja3li name te3ko sinon traja3 none
            # if user exist we will therow our validation error
            if user:
                raise ValidationError('That email is taken. Please choose a diffrent one.')

class PostForm(FlaskForm):
    title = StringField('Titre',validators=[DataRequired()])
    content = TextAreaField('Contenu',validators=[DataRequired()])
    submit = SubmitField('Publier')


class CourseForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    intro = TextAreaField('Introduction', validators=[DataRequired()])
    picture = FileField('Add Course Pictuer',validators=[FileAllowed(['jpg','png'])])
    # pdf = FileField('Add Course pdf file', validators=[FileAllowed(['pdf'])])
    #video = FileField('Add Course pdf video', validators=[FileAllowed(['mp4'])])
    submit = SubmitField('create course')

class ChapterForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    intro = TextAreaField('Introduction', validators=[DataRequired()])
    pdf = FileField('Add Chapter pdf file', validators=[FileAllowed(['pdf'])])
    video = FileField('Add Chapter video file', validators=[FileAllowed(['mp4'])])
    submit = SubmitField('create chapter')
class ChapterForm1(FlaskForm):
    Coursetitle = StringField('Course title', validators=[DataRequired()])
    title = StringField('Title', validators=[DataRequired()])
    intro = TextAreaField('Introduction', validators=[DataRequired()])
    pdf = FileField('Add Chapter pdf file', validators=[FileAllowed(['pdf'])])
    video = FileField('Add Chapter video file', validators=[FileAllowed(['mp4'])])
    submit = SubmitField('create chapter')







import os
import secrets

import plotly.utils
from PIL import Image
from flask import  render_template, url_for, flash, redirect,request,abort,request
from app.models import User,Post,Course,Chapters,CoronaDailyUpdateds
from app.forms import RegistrationForm,LoginForm,UpdateAccountForm,PostForm,CourseForm,ChapterForm,ChapterForm1
from app import app,db,bcrypt
from flask_login import login_user,current_user,logout_user,login_required
from datetime import datetime
from bs4 import BeautifulSoup
import requests
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json

import time
# each class is table in database
import numpy as np
from sklearn.preprocessing import PolynomialFeatures
from sklearn import linear_model

def conf_prediction():
    df = pd.read_csv('C:/Users/DELL/PycharmProjects/MedicalSite/app/static/csv/confirmed.csv')
    x = np.array(df['id']).reshape(-1, 1)
    y = np.array(df['total_cases']).reshape(-1, 1)
    plotlyFeat = PolynomialFeatures(degree=3)
    x = plotlyFeat.fit_transform(x)
    model = linear_model.ElasticNet(alpha=0.1, l1_ratio=0.9, selection='random', random_state=42)
    model.fit(x, y)
    y0 = model.predict(x)
    return int(model.predict(plotlyFeat.fit_transform([[df.shape[0]+2]]))[0])
def deaths_prediction():
    df = pd.read_csv('C:/Users/DELL/PycharmProjects/MedicalSite/app/static/csv/deaths.csv')
    x = np.array(df['id']).reshape(-1, 1)
    y = np.array(df['total_deaths']).reshape(-1, 1)
    plotlyFeat = PolynomialFeatures(degree=5)
    x = plotlyFeat.fit_transform(x)
    model = linear_model.Lasso(alpha=0.1,
              precompute=True,
#               warm_start=True,
              positive=True,
              selection='random',
              random_state=42)
    model.fit(x, y)
    y0 = model.predict(x)
    return int(model.predict(plotlyFeat.fit_transform([[df.shape[0] + 2]]))[0])

@app.route("/")
@app.route("/home", methods=['GET', 'POST'])
def home():
    conf = conf_prediction()
    dth = deaths_prediction()
    return render_template('home1.html', title='Home',conf=conf,dth=dth)


@app.route("/courses", methods=['GET', 'POST'])
def courses():
    courses = Course.query.all()
    l = []
    for c in courses:
        chap = Chapters.query.filter(Chapters.id_course == c.id).first()
        if chap != None:
            l.append(chap)
    team = zip(courses,l)

    return render_template('home.html',title='Courses page',team=team)



@app.route("/ASK", methods=['GET', 'POST'])
def ASK():
    posts = Post.query.all()
    return render_template('ASK.html', posts=posts)


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        #first we need to hash our code
        #!!! form.password.data way to retreve the data from password field
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data,email=form.email.data,password=hashed_password,workpost=dict(form.workpost.choices).get(form.workpost.data),Registration_Date=datetime.now())
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form=LoginForm()
    if form.validate_on_submit():
        #make sure the user exist
        user = User.query.filter_by(email=form.email.data).first()
        # make sure that is entering the right password
        if user and bcrypt.check_password_hash(user.password,form.password.data):
            # if the usename exist and the pass is correct we need to loged the user in
            login_user(user,remember=form.remember.data)
            # if the user is loged in we need to redirect the user to the home page
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            # ken login 8alet ray fama prob
            flash('Login Unsuccessful. Please check email and password','danger')
    # ba3 ma yflashi msg yrja3 login page again
    return render_template('login.html',title='login',form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))
#hajet li ynejm user yamlelhom access itha houa loged in
# we need to make our pic name random with random hex bech ma tetba9ch ma pic 3ana
# os.path.splitecxt(file) traj3lek file name wo extention teha
# root_path env variable ya3tina full path ta app te3na
# os.path.join bech nsobo image te3na
def save_picture(form_pic):
    random_hex = secrets.token_hex(8) # deja 3malelna generation ta name
    _,f_ext=os.path.splitext(form_pic.filename) # traj3lna extention ta file
    picture_fn=random_hex + f_ext
    picture_path = os.path.join(app.root_path,'static/profile_pics',picture_fn)

    output_size = (125,125)
    i = Image.open(form_pic)
    i.thumbnail(output_size)

    i.save(picture_path)
    return picture_fn


@app.route("/UpdateAccount",methods=['GET', 'POST'])
@login_required
def updateaccount():
    form = UpdateAccountForm()
    # we can update the username and email easly with sql alchemy useing current_user
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data) # saveing the pic in our static system
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!','success')
        return redirect(url_for('account',user_id=current_user.id))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email


    image_file = url_for('static',filename='profile_pics/' + current_user.image_file)
    return render_template('updateaccount.html', title='Account', image_file=image_file,form=form)

@app.route("/account/<int:user_id>")
def account(user_id):
    user = User.query.get_or_404(user_id)
    courses = Course.query.filter(Course.user_id == user_id).all()
    l=[]
    for c in courses:
        chap = Chapters.query.filter(Chapters.id_course == c.id).first()
        if chap != None:
            l.append(chap)

    team = zip(courses, l)
    return render_template('account.html', title=user.username,user=user,team=team)


@app.route("/post/new",methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title = form.title.data,content=form.content.data,author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your Post has been created!','success')
        return redirect(url_for('ASK'))
    return render_template('create_post.html',title='New Post',form=form,legend='nouveau poste')

@app.route("/post/<int:post_id>")
def post(post_id):
    # give me that post with id if not exist retun 404 page
    post = Post.query.get_or_404(post_id)
    return render_template('post.html',title=post.title,post=post)


@app.route("/post/<int:post_id>/update",methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    #abort() function that aborts a request with an HTTP error code early. It will also provide a plain black and white
    # error page for you with a basic description, but nothing fancy.
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!','success')
        return redirect(url_for('post',post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post', form=form,legend='Update Post')


@app.route("/post/<int:post_id>/delete",methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    # abort() function that aborts a request with an HTTP error code early. It will also provide a plain black and white
    # error page for you with a basic description, but nothing fancy.
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('ASK'))

def save_picture1(form_pic):
    random_hex = secrets.token_hex(8) # deja 3malelna generation ta name
    _,f_ext=os.path.splitext(form_pic.filename) # traj3lna extention ta file
    picture_fn=random_hex + f_ext
    picture_path = os.path.join(app.root_path,'static/course_pics',picture_fn)

    output_size = (125,125)
    i = Image.open(form_pic)
    i.thumbnail(output_size)

    i.save(picture_path)
    return picture_fn
def save_pdf(form_pdf):
    random_hex = secrets.token_hex(8) # deja 3malelna generation ta name
    _,f_ext=os.path.splitext(form_pdf.filename) # traj3lna extention ta file
    pdf_fn=random_hex + f_ext
    pdf_path = os.path.join(app.root_path,'static/course_files',pdf_fn)


    form_pdf.save(pdf_path)
    return pdf_fn
def save_mp4(form_mp4):
    random_hex = secrets.token_hex(8) # deja 3malelna generation ta name
    _,f_ext=os.path.splitext(form_mp4.filename) # traj3lna extention ta file
    mp4_fn=random_hex + f_ext
    mp4_path = os.path.join(app.root_path,'static/course_vids',mp4_fn)


    form_mp4.save(mp4_path  )
    return mp4_fn




@app.route("/course/costum",methods=['GET', 'POST'])
@login_required
def costum_course():
    return render_template('costum_course_page.html',title='Costum course')







@app.route("/course/new",methods=['GET', 'POST'])
@login_required
def new_course():
    form = CourseForm()

    if form.validate_on_submit():
        image_file = save_picture1(form.picture.data)
        #pdf_file= save_pdf(form.pdf.data)
        #video_file = save_mp4(form.video.data)
        course = Course(title = form.title.data,intro=form.intro.data,image_file=image_file,doctor=current_user)
        db.session.add(course)
        db.session.commit()
        flash('Your course has been created!','success')
        return redirect(url_for('home'))
    return render_template('create_course.html',title='New course',form=form,legend='New course')

@app.route("/course/<int:course_id>/<int:chapter_id>", methods=['GET', 'POST'])
def course(course_id,chapter_id):
    # give me that post with id if not exist retun 404 page
    chapters = Chapters.query.filter(Chapters.id_course == course_id).all()
    exact_chapter = Chapters.query.filter(Chapters.id == chapter_id).first()
    course = Course.query.get_or_404(course_id)

    return render_template('courselist.html',title=course.title,course=course,chapters=chapters,exact_chapter=exact_chapter)



@app.route("/course/<int:course_id>/update",methods=['GET', 'POST'])
@login_required
def update_course(course_id):
    course = Course.query.get_or_404(course_id)
    # abort() function that aborts a request with an HTTP error code early. It will also provide a plain black and white
    # error page for you with a basic description, but nothing fancy.
    if course.doctor != current_user:
        abort(403)
    form = CourseForm()
    if form.validate_on_submit():
        course.title = form.title.data
        course.intro = form.intro.data
        if form.picture.data:
            picture_file = save_picture1(form.picture.data)
            course.image_file = picture_file
        db.session.commit()
        flash('Your course has been updated!', 'success')
        return redirect(url_for('home'))
    elif request.method == 'GET':
        form.title.data = course.title
        form.intro.data = course.intro
    return render_template('create_course.html', title='Update Course', form=form ,legend='Update Course')



@app.route("/course/<int:course_id>/delete",methods=['POST'])
@login_required
def delete_course(course_id):
    course = Course.query.get_or_404(course_id)
    chapters = Chapters.query.filter(Chapters.id_course == course_id).all()
    # abort() function that aborts a request with an HTTP error code early. It will also provide a plain black and white
    # error page for you with a basic description, but nothing fancy.
    if course.doctor != current_user:
        abort(403)

    for chap in chapters:
     db.session.delete(chap)
     db.session.commit()

    db.session.delete(course)
    db.session.commit()
    flash('Your course has been deleted!', 'success')
    return redirect(url_for('home'))

@app.route("/chapter/<int:course_id>/new",methods=['GET', 'POST'])
@login_required
def new_chapter(course_id):
    form = ChapterForm()

    if form.validate_on_submit():
        pdf_file= save_pdf(form.pdf.data)
        video_file = save_mp4(form.video.data)
        chapter = Chapters(title = form.title.data,intro=form.intro.data,pdf_file=pdf_file,video_file=video_file,id_course=course_id)
        db.session.add(chapter)
        db.session.commit()
        flash('Your chapter has been created!','success')
        return redirect(url_for('home'))
    return render_template('create_chapter.html',title='New Chapter',form=form,legend='New chapter')
@app.route("/chapter/new",methods=['GET', 'POST'])
@login_required
def new_chapter1():
    form = ChapterForm1()

    if form.validate_on_submit():
        course = Course.query.filter(Course.title == form.Coursetitle.data).first()
        pdf_file = save_pdf(form.pdf.data)
        video_file = save_mp4(form.video.data)
        chapter = Chapters(title=form.title.data, intro=form.intro.data, pdf_file=pdf_file, video_file=video_file,id_course=course.id)
        db.session.add(chapter)
        db.session.commit()
        flash('Your chapter has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_chapter1.html', title='New Chapter', form=form, legend='New chapter')

def scraping_data():
    html_text = requests.get('https://www.worldometers.info/coronavirus/country/tunisia/').text
    soup =BeautifulSoup(html_text,'lxml')
    main_div = soup.find('div', class_='col-md-8')
    maincounter_numbers = main_div.find_all('div', class_='maincounter-number')
    listy=maincounter_numbers
    update = CoronaDailyUpdateds(confirmed=int(listy[0].text.replace(',', '')),
                                 recoverd=int(listy[2].text.replace(',', '')),
                                 deaths=int(listy[1].text.replace(',', '')))
    db.session.add(update)
    db.session.commit()
import pandas as pd
def datafarme_conv():
    corona = CoronaDailyUpdateds.query.all()
    col_conf,col_deaths,col_recov,col_date = [],[],[],[]
    col_date = [ c.date.strftime('%Y-%m-%d') for c in corona ]
    for c in corona:
        col_conf.append(c.confirmed)
        col_deaths.append(c.deaths)
        col_recov.append(c.recoverd)
    dict_conf = {'date':col_date,'confirmed': col_conf}
    dict_deaths = {'date': col_date, 'deaths': col_deaths}
    dict_recov = {'date': col_date, 'recoverd': col_recov}
    return pd.DataFrame(data=dict_conf),pd.DataFrame(data=dict_deaths),pd.DataFrame(data=dict_recov)


def scattter_plot():
    conf, deth, recov = datafarme_conv()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=conf['date'], y=conf['confirmed'], mode='lines+markers', name='Confirmed',
                             line=dict(color="Orange", width=2)))
    fig.add_trace(go.Scatter(x=recov['date'], y=recov['recoverd'], mode='lines+markers', name='Recovered',
                             line=dict(color="Green", width=2)))
    fig.add_trace(go.Scatter(x=deth['date'], y=deth['deaths'], mode='lines+markers', name='Deaths',
                             line=dict(color="Red", width=2)))
    fig.update_layout(title='Tunisia Covid-19 Cases', xaxis_tickfont_size=14, yaxis=dict(title='Number of Cases'))
    graph1JSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graph1JSON

#color pallette



def bar_plot():
    cnf = '#393e46'
    dth = '#ff2e63'
    rec = '#21bf73'
    act = '#fe9801'
    conf, deth, recov = datafarme_conv()
    fig_c = px.bar(conf, x='date', y='confirmed', color_discrete_sequence=[act])
    fig_d = px.bar(deth, x='date', y='deaths', color_discrete_sequence=[dth])
    fig = make_subplots(rows=1, cols=2, shared_xaxes=False, horizontal_spacing=0.1,
                        subplot_titles=('Confirmed Cases', 'Deaths Cases'))
    fig.add_trace(fig_c['data'][0], row=1, col=1)
    fig.add_trace(fig_d['data'][0], row=1, col=2)
    fig.update_layout(height=480)
    graph2JSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graph2JSON


def update_csv():
    df = pd.read_csv('C:/Users/DELL/PycharmProjects/MedicalSite/app/static/csv/confirmed.csv')
    df1 = pd.read_csv('C:/Users/DELL/PycharmProjects/MedicalSite/app/static/csv/deaths.csv')
    corona = db.session.query(CoronaDailyUpdateds).order_by(CoronaDailyUpdateds.id.desc()).first()
    if (float(corona.confirmed)!=df['total_cases'][df.shape[0]-1]):
        dict={'Unnamed: 0':df.shape[0],'id':float(df.shape[0]),'total_cases':float(corona.confirmed)}
        df = df.append(dict, ignore_index=True)
        df.to_csv('C:/Users/DELL/PycharmProjects/MedicalSite/app/static/csv/confirmed.csv')
    if (float(corona.deaths) != df1['total_deaths'][df1.shape[0]-1]):
        dict = {'id':df1.shape[0], 'total_deaths':float(corona.deaths)}
        df1 = df1.append(dict, ignore_index=True)
        df1.to_csv('C:/Users/DELL/PycharmProjects/MedicalSite/app/static/csv/deaths.csv')



@app.route("/corona_dashbord")
def corona_dash():
        test = CoronaDailyUpdateds.query.all()
        a = True
        for t in test:
            if t.date.year == datetime.now().year and t.date.month == datetime.now().month and  t.date.day == datetime.now().day :
                a = False
                break
        if a == False :

            corona =db.session.query(CoronaDailyUpdateds).order_by(CoronaDailyUpdateds.id.desc()).first()
            daily = CoronaDailyUpdateds.query.order_by(CoronaDailyUpdateds.id.desc()).limit(2).all()
            graph1JSON = scattter_plot()
            graph2JSON = bar_plot()

            return render_template('Corona_Dashbord.html',title="dahsbord",corona=corona, graph1JSON= graph1JSON,  graph2JSON=graph2JSON,daily=daily)
        else:
            scraping_data()
            update_csv()
            corona = db.session.query(CoronaDailyUpdateds).order_by(CoronaDailyUpdateds.id.desc()).first()
            graph1JSON = scattter_plot()
            graph2JSON = bar_plot()
            return render_template('Corona_Dashbord.html',title="dahsbord",corona=corona,graph1JSON= graph1JSON,graph2JSON=graph2JSON)


import dash_core_components as dcc
import dash_html_components as html
@app.route("/density_map")
def density_map():
    tunisia_states = pd.read_csv('C:/Users/DELL/Downloads/tn.csv')
    fig = px.density_mapbox(tunisia_states, lat='lat', lon='lng', hover_name='country', hover_data=['population'],
                            color_continuous_scale='Portland', radius=7, height=900,width=600,zoom=5    ,center={"lat": 36.862499 , "lon":11.195556 })
    fig.update_layout(mapbox_style="stamen-terrain", mapbox_center_lon=10)

    div = fig.to_html(full_html=False)
    return render_template('density_map.html', div_placeholder=div)

@app.route("/protocole")
def protocole():
    return render_template('protocole.html')
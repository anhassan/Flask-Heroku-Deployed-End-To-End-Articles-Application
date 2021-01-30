from flask import Flask, render_template, redirect, \
    url_for, request, redirect, flash, session
from flask_bootstrap import Bootstrap
from data import Articles
from registration_form import RegistrationForm
from login_form import LoginForm
from article_form import ArticleForm
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from passlib.hash import sha256_crypt as sha256
from flask_login import LoginManager, login_user, login_required, UserMixin
import sqlite3, logging

# Instanciating the App
app = Flask(__name__)
# Does not list out the warnings
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Entering the URI of the Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'

# Using Bootstrap in Flask for styling
Bootstrap(app)
# Setting up a secret token for Session variable
app.config['SECRET_KEY'] = 'thisismysecretkey!'
db = SQLAlchemy(app)

# Setting up the login manager for Authorization
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


# Model for members registered in the App
class Member(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    email = db.Column(db.String(20))
    username = db.Column(db.String(20))
    password = db.Column(db.String(20))
    date = db.Column(db.DateTime, default=datetime.now)


# Model for Articles inputed by the Members of the App
class Articles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    author = db.Column(db.String(20))
    body = db.Column(db.Text)
    date = db.Column(db.DateTime, default=datetime.now)


@login_manager.user_loader
def load_user(user_id):
    return Member.query.get(user_id)


# Home Route
@app.route('/')
def home():
    return render_template("home.html")


# About Route
@app.route('/about')
def about():
    return render_template("about.html")


# All the articles are listed in this route
@app.route('/articles')
def articles():
    # Fetching all the articles in the database
    articles = Articles.query.all()
    # Displaying all the articles
    if (len(articles) > 0):
        return render_template("articles.html", articles=articles)
    else:
        error = "No Articles Available"
        return render_template("articles.html", error=error)


# Details of a particular article
@app.route('/article/<int:id>')
def article(id):
    article = Articles.query.filter_by(id=id).first()
    return render_template("article.html", article=article)


# User Registration Route
@app.route('/register', methods=["GET", "POST"])
def registor():
    registration_form = RegistrationForm(request.form)
    if registration_form.validate_on_submit() and request.method == "POST":
        # Entering member credentials in the database
        member = Member(name=request.form["name"], email=request.form["email"],
                        username=request.form["username"], password=str(request.form["password"]))
        db.session.add(member)
        db.session.commit()
        flash('You are registered and can log in')
        return redirect(url_for('login'))
    return render_template("register.html", form=registration_form)


# Login Route
@app.route('/login', methods=["GET", "POST"])
def login():
    login_form = LoginForm(request.form)
    if request.method == "POST" and login_form.validate_on_submit():
        matched_member = Member.query.filter_by(username=request.form["username"]).first()
        if matched_member is None:
            # Not a member. Needs to get registered before login.
            error = "Invalid Username"
            return render_template("login.html", error=error, form=login_form)

        if matched_member.password == request.form["password"]:
            # Password match successful
            session['logged_in'] = True
            session['username'] = matched_member.username
            login_user(matched_member)
            flash("Welcome to the Dashboard")
            return redirect(url_for('dashboard'))
        else:
            # Incorrect Password
            error = "Incorrect Password"
            return render_template("login.html", error=error, form=login_form)

    return render_template("login.html", form=login_form)


# Dashboard for Members(Authorized)
@app.route('/dashboard')
@login_required
def dashboard():
    # Displays articles for the user logged in
    member = Member.query.filter_by(username=session['username']).first()
    articles = Articles.query.filter_by(author=member.name).all()
    if (len(articles) > 0):
        return render_template("dashboard.html", articles=articles)
    else:
        error = "No Article published by " + member.name
        return render_template("dashboard.html", error=error)


# Adding Articles Route(Authorized)
@app.route('/add_article', methods=["GET", "POST"])
@login_required
def add_article():
    article_form = ArticleForm(request.form)
    if request.method == "POST" and article_form.validate_on_submit():
        member = Member.query.filter_by(username=session['username']).first()
        article = Articles(title=request.form["title"], body=request.form["body"], author=member.name)
        db.session.add(article)
        db.session.commit()
        flash("Article Added")
        return redirect(url_for('dashboard'))
    return render_template("addArticles.html", form=article_form)


# Editing a particular Article Route(Authorized)
@app.route("/edit_article/<int:id>", methods=["GET", "POST"])
@login_required
def edit_article(id):
    article_form = ArticleForm(request.form)
    article = Articles.query.filter_by(id=id).first()
    # Displaying the already present article details in the form
    article_form.title.data = article.title
    article_form.body.data = article.body

    # Updating the Article Content
    if request.method == "POST":
        updated_title = request.form["title"]
        updated_body = request.form["body"]

        article.title = updated_title
        article.body = updated_body
        db.session.commit()
        flash("Article Edited")
        return redirect(url_for('dashboard'))
    return render_template("editArticles.html", form=article_form)


# Deleting a particular Article(Authorized)
@app.route("/delete_article/<int:id>", methods=["GET", "POST"])
@login_required
def delete_article(id):
    Articles.query.filter_by(id=id).delete()
    db.session.commit()
    flash("Article Deleted")
    return redirect(url_for('dashboard'))


@app.route('/logout')
@login_required
def logout():
    if "logged_in" in session:
        session.clear()
        flash("You have successfully logged out")
        return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)

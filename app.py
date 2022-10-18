import os
import requests
import json

from flask import Flask, json, render_template, request, redirect, session,flash
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash


app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True

app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.db'
db = SQLAlchemy(app)

class users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    hash = db.Column(db.String(120), unique=True, nullable=False)

class movies(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.String(80), unique=False, nullable=False)
    title = db.Column(db.String(80), nullable=False)
    imageurl = db.Column(db.String(500), nullable=False)
    watchlist = db.Column(db.Boolean, default=False)
    favlist = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer,  db.ForeignKey('users.id'),
        nullable=False)

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")

api_key = os.environ.get("API_KEY")

@app.route("/", methods=["GET", "POST"])
def index():
    if session.get("user_id") == None:
        return redirect("/login")
    res_1 = requests.get(f"https://imdb-api.com/en/API/Top250Movies/{api_key}")
    topratedmovies = res_1.json()
    return render_template("index.html",trm=topratedmovies)


@app.route("/topratedmovies")
def trm():
    res = requests.get(f"https://imdb-api.com/en/API/Top250Movies/{api_key}")
    data = res.json()
    return render_template("mostpopular.html",data=data)


@app.route("/search", methods=["GET", "POST"])
def search():
    title = request.args.get("q")
    print(title)
    if not title:
        return render_template("search.html", data=None)
    req = requests.get(
        f"https://imdb-api.com/en/API/SearchTitle/{api_key}/{title}")
    data = json.loads(req.content)
    return render_template("search.html", data=data['results'])

@app.route("/person/<string:id>")
def person(id):
    res = requests.get(f"https://imdb-api.com/API/Name/{api_key}/{id}")
    data = res.json()
    return render_template("person.html",data=data)


@app.route("/title/<string:id>", methods=["GET", "POST"])
def title(id):
    if request.method == "POST":
        if request.form.get("id"):
            movie_id = request.form.get("id")
            res = requests.get(f"https://imdb-api.com/API/YouTubeTrailer/{api_key}/{movie_id}")
            url_data = res.json()
            return redirect(url_data['videoUrl'])
        if request.form.get('watchlist'):
            movie_id = request.form.get("watchlist")
            res = requests.get(f"https://imdb-api.com/en/API/Title/{api_key}/{movie_id}")
            data = res.json()
            mdata = db.session.query(movies).filter(movies.user_id==session.get('user_id'),movies.movie_id==id).first()
            if not mdata:
                db.session.add(movies(
                    movie_id=data['id'],
                    title=data['title'],
                    imageurl=data['image'],
                    watchlist=True,
                    favlist=False,
                    user_id=session.get("user_id")
                ))
                db.session.commit()
                mdata = db.session.query(movies).filter(movies.user_id==session.get('user_id'),movies.movie_id==id).first()
            if mdata.favlist == True and mdata.watchlist == False:
                mdata.favlist = False
                mdata.watchlist = True
                db.session.commit()
            mdata = db.session.query(movies).filter(movies.user_id==session.get('user_id'),movies.movie_id==id).first()
            return render_template("title.html", data=data,watchlisted=mdata.watchlist,faved=mdata.favlist)
        elif request.form.get('favlist'):
            movie_id = request.form.get("favlist")
            res = requests.get(f"https://imdb-api.com/en/API/Title/{api_key}/{movie_id}")
            data = json.loads(res.content)
            mdata = db.session.query(movies).filter(movies.user_id==session.get('user_id'),movies.movie_id==id).first()
            if not mdata:
                db.session.add(movies(
                    movie_id=data['id'],
                    title=data['title'],
                    imageurl=data['image'],
                    watchlist=False,
                    favlist=True,
                    user_id=session.get("user_id")
                ))
                db.session.commit()
                mdata = db.session.query(movies).filter(movies.user_id==session.get('user_id'),movies.movie_id==id).first()
            if mdata.watchlist == True and mdata.favlist == False:
                mdata.watchlist = False
                mdata.favlist = True
                db.session.commit()
            mdata = db.session.query(movies).filter(movies.user_id==session.get('user_id'),movies.movie_id==id).first()
            return render_template("title.html", data=data,watchlisted=mdata.watchlist,faved=mdata.favlist)

    else:
        if not id:
            return redirect("/")
        res = requests.get(
            f"https://imdb-api.com/en/API/Title/{api_key}/{id}")
        data = json.loads(res.content)
        mdata = db.session.query(movies).filter(movies.user_id==session.get('user_id'),movies.movie_id==data['id']).first()
        if not mdata:
            return render_template("title.html", data=data,watchlisted=False,faved=False)
        return render_template("title.html", data=data,watchlisted=mdata.watchlist,faved=mdata.favlist)


@app.route("/watchlist", methods=["POST","GET"])
def watchlist():
    if request.method == "POST":
        id = request.form.get('remove')
        movie = db.session.query(movies).filter(movies.user_id==session.get('user_id'),movies.movie_id==id,movies.watchlist==True).first()
        db.session.delete(movie)
        db.session.commit()
        data = db.session.query(movies).filter(movies.user_id==session.get('user_id'),movies.watchlist==True).all()
        if not data:
            return render_template("watchlist.html",data=None)
        return render_template("watchlist.html",data=data)
    else:
        data = db.session.query(movies).filter(movies.user_id==session.get('user_id'),movies.watchlist==True).all()
        if not data:
            return render_template("watchlist.html",data=None)
        return render_template("watchlist.html",data=data)


@app.route("/favlist", methods=["POST","GET"])
def favlist():
    if request.method == "POST":
        id = request.form.get('remove')
        movie = db.session.query(movies).filter(movies.user_id==session.get('user_id'),movies.movie_id==id,movies.favlist==True).first()
        db.session.delete(movie)
        db.session.commit()
        data = db.session.query(movies).filter(movies.user_id==session.get('user_id'),movies.favlist==True).all()
        if not data:
            return render_template("favlist.html",data=None)
        return render_template("favlist.html",data=data)
    else:
        data = db.session.query(movies).filter(movies.user_id==session.get('user_id'),movies.favlist==True).all()
        if not data:
            return render_template("favlist.html",data=None)
        return render_template("favlist.html",data=data)

@app.route("/profile")
def profile():
    data = []
    i = 0
    fdata = db.session.query(movies).filter(movies.user_id==session.get('user_id'),movies.favlist==True).all()
    if not fdata:
        return render_template("profile.html",data=None)
    for item in fdata:
        res = requests.get(f"https://imdb-api.com/en/API/Title/{api_key}/{item.movie_id}")
        mdata = res.json()
        for j in range(3):
            data.append({})
            data[i]["id"] = mdata["similars"][j]["id"]
            data[i]["title"] = mdata["similars"][j]["fullTitle"]
            data[i]["image"] = mdata["similars"][j]["image"]
            i += 1
    return render_template("profile.html", data=data)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("username")
        if not name:
            return "must provide username"
        if "'" in name or ";" in name:
            return "invalid character in username"
        found_user = users.query.filter_by(username=name).first()
        if found_user:
            return "username already in use"
        password = request.form.get("password")
        if not password:
            return "must provide password"
        confirmation_password = request.form.get("confirmation")
        if not confirmation_password:
            return "must provide confirmation password"
        if password != confirmation_password:
            return "passwords do not match"
        hashed_password=generate_password_hash(password)
        user = users(username=name, hash=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash("Account Created Successfully.")
        return redirect("/login")
    else:
        return render_template("register.html")

@ app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()

    if request.method == "POST":
        name = request.form.get('username')
        if not name:
            return "enter username"

        password = request.form.get('password')
        if not password:
            return "enter password"
        
        user_data = users.query.filter_by(username=name).first()
        if not user_data or not check_password_hash(user_data.hash,password):
            return "invalid username or password"
        session["user_id"]= user_data.id
        session["username"]= user_data.username

        return redirect("/")

    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)

@app.before_first_request
def create_tables():
    db.create_all()
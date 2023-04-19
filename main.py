from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

MOVIE_DB_API_KEY = "482c4ecc8469c0f8e5b76a8f2c24e94e"
MOVIE_DB_SEARCH_URL = "https://api.themoviedb.org/3/search/movie"
MOVIE_DB_INFO_URL = "https://api.themoviedb.org/3/movie"
MOVIE_DB_IMAGE_URL = "https://image.tmdb.org/t/p/w500"


app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)
#------------------------------------#######-----------------------------------#

#Creating Forms
class UpdateForm(FlaskForm):
    rating = StringField(label="Your Rating Out Of 10 e.g. 7.4",name="rate",  validators=[DataRequired()])
    review = StringField(label="Your Review",name="review", validators=[DataRequired()])
    button = SubmitField(label="Done")


class AddForm(FlaskForm):
    movie_title = StringField(label="Movie Title",name="movietitle", validators=[DataRequired()])
    add_button = SubmitField(label="Add Movie")


#------------------------------------#######-----------------------------------#

#Creating SQL File
app.app_context().push()
app.config['SQLALCHEMY_DATABASE_URI']="sqlite:///movie-details.db"
db = SQLAlchemy(app)

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(500), nullable=False)
    rating = db.Column(db.Float, nullable=True)
    ranking = db.Column(db.Integer,  nullable=True)
    review = db.Column(db.String(250),  nullable=True)
    img_url = db.Column(db.String(500), nullable=False)

db.create_all()
#------------------------------------#######-----------------------------------#

# new_movie = Movie(
#         title="Phone Booth",
#         year=2002,
#         description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
#         rating=7.3,
#         ranking=10,
#         review="My favourite character was the caller.",
#         img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
#     )
# db.session.add(new_movie)
# db.session.commit()
#-------------------------#####--------------------------#



@app.route("/")
def home():
    all_movies = db.session.query(Movie).all()
    mov_len = len(all_movies)
    for i in range(len(all_movies)):
        all_movies[i].ranking = len(all_movies) - i
    db.session.commit()
    return render_template("index.html", movies=all_movies, length=mov_len)

#------------------------------------#######-----------------------------------#
@app.route("/edit<movie_id>", methods=["POST","GET"])
def edit(movie_id):
    if request.method == "POST":
        your_rating = request.form["rate"]
        your_review = request.form["review"]
        movie = Movie.query.get(movie_id)
        movie.rating = your_rating
        movie.review = your_review
        db.session.commit()
        return redirect(url_for("home"))
    form = UpdateForm()
    movie = Movie.query.get(movie_id)
    return render_template("edit.html", form=form, movie=movie)

@app.route("/delete<movie_id>")
def delete(movie_id):
    movie = Movie.query.get(movie_id)
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for("home"))
#------------------------------------#######-----------------------------------#

@app.route("/add", methods=["POST","GET"])
def add():
    form = AddForm()
    if request.method == "POST":
        movie_title = request.form["movietitle"]
        response = requests.get(MOVIE_DB_SEARCH_URL, params={"api_key": MOVIE_DB_API_KEY, "query": movie_title})
        data = response.json()["results"]
        return render_template("select.html", options=data)
    return render_template("add.html", form=form)

#------------------------------------#######-----------------------------------#
@app.route("/find")
def find_movie():
    movie_api_id = request.args.get("id")
    if movie_api_id:
        movie_api_url = f"{MOVIE_DB_INFO_URL}/{movie_api_id}"
        #The language parameter is optional, if you were making the website for a different audience
        #e.g. Hindi speakers then you might choose "hi-IN"
        response = requests.get(movie_api_url, params={"api_key": MOVIE_DB_API_KEY, "language": "en-US"})
        data = response.json()
        new_movie = Movie(
            title=data["title"],
            #The data in release_date includes month and day, we will want to get rid of.
            year=data["release_date"].split("-")[0],
            img_url=f"{MOVIE_DB_IMAGE_URL}{data['poster_path']}",
            description=data["overview"],
            #rating=5.0,
            #review="-",
            #ranking=0
        )
        db.session.add(new_movie)
        db.session.commit()
        movie_sql_id = Movie.query.filter_by(title=data["title"]).first().id
        return redirect(url_for("edit", movie_id=movie_sql_id))
#------------------------------------#######-----------------------------------#



if __name__ == '__main__':
    app.run(debug=True)

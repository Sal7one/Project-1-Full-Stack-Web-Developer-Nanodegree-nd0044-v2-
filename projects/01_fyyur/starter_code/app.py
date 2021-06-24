#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
from os import error
from typing import final
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database

# Migrations
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    genres = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String)
    shows = db.relationship('Show', backref='venue')


class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String)
    shows = db.relationship('Show', backref='artist')

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.


class Show(db.Model):
    __tablename__ = 'show'

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'artist.id'), nullable=False)

    start_time = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow)
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    currentTime = datetime.now()
    data = []
    citites = set()
    try:
        venues = db.session.query(Venue)
        for venue in venues:
            citites.add((venue.city, venue.state))

        for place_deatiles in citites:
            allvenues = []
            for venue in venues:
                # Same city and state
                if (venue.city == place_deatiles[0]) and (venue.state == place_deatiles[1]):

                    all_venue_shows = db.session.query(
                        Show).filter_by(venue_id=venue.id).all()
                    # Check if the the show has passed
                    upcoming_shows = 0
                    for a_show in all_venue_shows:
                        if a_show.start_time > currentTime:
                            upcoming_shows += 1

                    # Add venue of the same state, city
                    allvenues.append({
                        "id": venue.id,
                        "name": venue.name,
                        "num_upcoming_shows": upcoming_shows
                    })

            data.append({
                "city": place_deatiles[0],
                "state": place_deatiles[1],
                "venues": allvenues
            })

    except error:
        print(error)
    finally:
        db.session.close()

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    response = {
        "count": 1,
        "data": [{
            "id": 2,
            "name": "The Dueling Pianos Bar",
            "num_upcoming_shows": 0,
        }]
    }
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id

    data = {}
    try:
        current_time = datetime.now()
        upcoming_shows = []
        past_shows = []

        # Get veneue and related shows
        venue = db.session.query(Venue).get(venue_id)
        allshows = db.session.query(Show).filter_by(venue_id=venue_id).all()

        for show in allshows:
            # Get artist info
            artist = db.session.query(Artist).get(show.artist_id)
            a_show = {
                "artist_id": artist.id,
                "artist_name": artist.name,
                "artist_image_link": artist.image_link,
                "start_time": str(show.start_time)
            }
            if show.start_time > current_time:
                upcoming_shows.append(a_show)
            else:
                past_shows.append(a_show)

        venue.genres = venue.genres.split(",")
        data = {
            "id": venue.id,
            "name": venue.name,
            "address": venue.address,
            "genres": venue.genres,
            "city": venue.city,
            "state": venue.state,
            "phone": venue.phone,
            "facebook_link": venue.facebook_link,
            "seeking_talent": venue.seeking_talent,
            "seeking_description": venue.seeking_description,
            "image_link": venue.image_link,
            "past_shows": past_shows,
            "upcoming_shows": upcoming_shows,
            "past_shows_count": len(past_shows),
            "upcoming_shows_count": len(upcoming_shows)

        }
    except error:
        flash("Error occured Cant fill user data")
        print(error)
    finally:
        db.session.close()

   # data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    data = request.form
    try:
        genere_joiner = ","
        form = VenueForm()

        # Get data from user

        venue_name = data['name'].strip()
        venue_city = data['city'].strip()
        venue_state = data['state'].strip()
        venue_address = data['address'].strip()
        phone_num = data['phone'].strip()
        genres = request.form.getlist('genres')
        genres = genere_joiner.join(genres)
        facebook_link = data['facebook_link'].strip()
        image_link = data['image_link'].strip()
        website_link = data['website_link'].strip()
        seeking_talent = True if request.form.get(
            "seeking_talent", False) == "y" else False
        seeking_description = data['seeking_description'].strip()

        # Create venue object
        thevenue = Venue(name=venue_name, city=venue_city, state=venue_state,
                         address=venue_address, phone=phone_num, genres=genres,
                         image_link=image_link,  facebook_link=facebook_link, website_link=website_link, seeking_talent=seeking_talent,
                         seeking_description=seeking_description
                         )
        
        # Add to Db
        db.session.add(thevenue)
        db.session.commit()
        flash('Venue ' + venue_name + ' was successfully listed!')

    except error:
        # Error handling
        venue_name = request.form['name']
        db.session.rollback()
        print("Insert error: ", error)
        flash('An error occurred. Venue ' +
              venue_name + ' could not be listed.')

    return render_template('pages/home.html')


@app.route('/venues/<venue_id>/delete', methods=['GET'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail

    try:
        print("deleting id ", venue_id)
        # Delete the show first
        show = db.session.query(Show).get(venue_id)
        db.session.delete(show)

        # Delete venue now
        venue = db.session.query(Venue).get(venue_id)
        db.session.delete(venue)
        db.session.commit()
    except error:
        db.session.rollback()
        print("error inside")
    finally:
        db.session.close()
        return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------

@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    try:
        artist = db.session.query(Artist).all()
    except:
        print("error")
    finally:
        db.session.close()

    return render_template('pages/artists.html', artists=artist)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    response = {
        "count": 1,
        "data": [{
            "id": 4,
            "name": "Guns N Petals",
            "num_upcoming_shows": 0,
        }]
    }
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id

    data = {}
    try:
        current_time = datetime.now()
        upcoming_shows = []
        past_shows = []

        # Get veneue and related shows
        artist = db.session.query(Artist).get(artist_id)
        allshows = db.session.query(Show).filter_by(artist_id=artist_id).all()

        for show in allshows:
            # Get artist info
            venue = db.session.query(Venue).get(show.venue_id)
            a_show = {
                "venue_id": venue.id,
                "venue_name": venue.name,
                "venue_image_link": venue.image_link,
                "start_time": str(show.start_time)
            }
            if show.start_time > current_time:
                upcoming_shows.append(a_show)
            else:
                past_shows.append(a_show)

        artist.genres = artist.genres.split(",")
        data = {
            "id": artist.id,
            "name": artist.name,
            "genres": artist.genres,
            "city": artist.city,
            "state": artist.state,
            "phone": artist.phone,
            "facebook_link": artist.facebook_link,
            "seeking_venue": artist.seeking_venue,
            "seeking_description": artist.seeking_description,
            "image_link": artist.image_link,
            "past_shows": past_shows,
            "upcoming_shows": upcoming_shows,
            "past_shows_count": len(past_shows),
            "upcoming_shows_count": len(upcoming_shows),
        }
    except error:
        print(error)
        flash("Error occured Cant fill user data")
    finally:
        db.session.close()

    #data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    try:
        artist = db.session.query(Artist).get(artist_id)
        artist.genres = artist.genres.split(",")
        form = ArtistForm(obj=artist)
    except:
        flash("Error occured Cant fill user data")
    finally:
        db.session.close()

    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes

    data = request.form
    try:
        artist = db.session.query(Artist).get(artist_id)
        genere_joiner = ","
        artist.name = data['name'].strip()
        artist.city = data['city'].strip()
        artist.state = data['state'].strip()
        artist.phone = data['phone'].strip()
        genres = request.form.getlist('genres')
        artist.genres = genere_joiner.join(genres)
        artist.facebook_link = data['facebook_link'].strip()
        artist.image_link = data['image_link'].strip()
        artist.website_link = data['website_link'].strip()
        artist.seeking_venue = True if request.form.get(
            "seeking_venue", False) == "y" else False
        artist.seeking_description = data['seeking_description'].strip()

        db.session.commit()
    except error:
        flash("Something went wrong")
        print(error)
        db.session.rollback()
    finally:
        db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):

    # TODO: populate form with values from venue with ID <venue_id>
    try:
        venue = db.session.query(Venue).get(venue_id)
        venue.genres = venue.genres.split(",")
        form = VenueForm(obj=venue)
    except:
        flash("Error occured Cant fill user data")
    finally:
        db.session.close()

    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):

    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    # use the form to vaildate data

    data = request.form
    form = VenueForm(data)
    try:
        if form.validate():
            print("Yup good stuff")
        venue = db.session.query(Venue).get(venue_id)
        genere_joiner = ","
        venue.name = data['name'].strip()
        venue.city = data['city'].strip()
        venue.state = data['state'].strip()
        venue.address = data['address'].strip()
        venue.phone = data['phone'].strip()
        genres = request.form.getlist('genres')
        venue.genres = genere_joiner.join(genres)
        venue.facebook_link = data['facebook_link'].strip()
        venue.image_link = data['image_link'].strip()
        venue.website_link = data['website_link'].strip()
        venue.seeking_talent = True if request.form.get(
            "seeking_talent", False) == "y" else False
        venue.seeking_description = data['seeking_description'].strip()

        db.session.commit()
    except:
        flash("Something went wrong")
        db.session.rollback()
    finally:
        db.session.close()

    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():

    # Save Form data
    data = request.form
    try:

        # Join the generes as string with a symbol betweet them ","
        genere_joiner = ","
        artist_name = data['name'].strip()
        artist_city = data['city'].strip()
        artist_state = data['state'].strip()
        phone_num = data['phone'].strip()
        genres = request.form.getlist('genres')
        genres = genere_joiner.join(genres)
        facebook_link = data['facebook_link'].strip()
        image_link = data['image_link'].strip()
        website_link = data['website_link'].strip()
        seeking_venue = True if request.form.get(
            "seeking_venue", False) == "y" else False
        seeking_description = data['seeking_description'].strip()

        # Create object from Artist model
        theartist = Artist(
            name=artist_name, city=artist_city, state=artist_state,
            phone=phone_num, genres=genres,
            image_link=image_link,  facebook_link=facebook_link, website_link=website_link, seeking_venue=seeking_venue,
            seeking_description=seeking_description
        )

        # Post to DB and success message
        db.session.add(theartist)
        db.session.commit()
        flash('Artist ' + artist_name + ' was successfully listed!')

    except error:
        # Error handling

        # rollback previous DB actions
        db.session.rollback()

        # Error
        artist_name = request.form['name']
        print("Insert error: ", error)
        flash('An error occurred. Artist ' +
              artist_name + ' could not be listed.')
    finally:
        db.session.close()

    return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------


@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    shows = db.session.query(Show).all()
    data = []
    try:
        for a_show in shows:
            artist = db.session.query(Artist).get(a_show.artist_id)
            venue = db.session.query(Venue).get(a_show.venue_id)
            show_Object = {
                "venue_id": venue.id,
                "venue_name": venue.name,
                "artist_id": artist.id,
                "artist_name": artist.name,
                "artist_image_link": artist.image_link,
                "start_time": (str(a_show.start_time))
            }
            data.append(show_Object)
        return render_template('pages/shows.html', shows=data)
    except error:
        print("Error")
        print(error)
        flash("No show found")
        return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead
    try:
        artist_id = request.form['artist_id']
        venue_id = request.form['venue_id']
        start_time = request.form['start_time']

        show = Show(artist_id=artist_id, venue_id=venue_id,
                    start_time=start_time)
        db.session.add(show)
        db.session.commit()
        # on successful db insert, flash success
        flash('Show was successfully listed!')

    except:
        db.session.rollback()
        flash('An error occured. show could not be listed, Double check the venue and artist IDs')
    finally:
        db.session.close()

    return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''

#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from datetime import date
import json
from os import name
from re import S, X
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_migrate import Migrate
from sqlalchemy.orm import relationship
from flask_wtf import Form
from sqlalchemy.sql.elements import Null
from sqlalchemy.sql.expression import false, true
from forms import *
import sys
# import all models in models .. venue,artist and show
from models import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy()
db.init_app(app)
migrate = Migrate(app, db)
# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
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
  city_state = db.session.query(Venue.city,Venue.state).group_by(Venue.city,Venue.state)
  venues = Venue.query.all()
  data_dict = {}
  
  data_dict_venue = {}
  # data_dict_venue_list = []
  
  data=[]
  
  for ct in city_state:
      data_dict_venue_list = []

      for venue in venues:
        # data_dict_venue_list = []
        if ct.city == venue.city and ct.state == venue.state:
          data_dict_venue = {
               "id": venue.id,
                "name": venue.name,
                "num_upcoming_shows": 0}
          data_dict_venue_list.append(data_dict_venue)
      data_dict={
        "city": ct.city,
        "state": ct.state,
        "venues": data_dict_venue_list}
      data.append(data_dict)
           
  

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  # form = VenueForm()
  name = request.form['search_term']
  # search = "%{}%".format(name)
  venues = Venue.query.filter(Venue.name.ilike("%"+name+"%")).all()
  count = 0
  data = []
  response ={}
  for venue in venues:
    data_dict = {
        "id":venue.id,
        "name":venue.name,
        "num_upcoming_shows":0
                 }
    data.append(data_dict)
    count += 1

  response={
    "count": count,
    "data": data
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  # venue = Venue.query.get(venue_id)
  # shows = Show.query.filter_by(venue_id=venue_id).all()
  # using join to show venues
  
  # i used outer join to prefent crash if there is not show attached with the venue
  venue = db.session.query(Venue,Show).outerjoin(Show, Show.venue_id == Venue.id).filter(Venue.id == venue_id).all()
  # venue,shows = venue_show
  print("*****************************************")
  print(venue[0][1])
  # print(venue[0][0].id)
  past_show = []
  upcoming_show = []
  
  # format up comming show and past show 
  # this will excute if there is show for the venue that is selected
  if venue[0][1]:
    for _,show in venue:
      artist = Artist.query.get(show.artist_id)
      if show.start_time  < datetime.now():
        p_show = {
          "artist_id": show.artist_id,
          "artist_name": artist.name,
          "artist_image_link": artist.image_link,
          "start_time": str(show.start_time)}
        past_show.append(p_show)
      else:
        u_show = {
          "artist_id": show.artist_id,
          "artist_name": artist.name,
          "artist_image_link": artist.image_link,
          "start_time": str(show.start_time)}
        upcoming_show.append(u_show)
  # format genres to convert it to list
  x1 = venue[0][0].genre[1:-1]
  x1 = str(x1)
  x1 = x1.split(',')
  genres_list = x1

  data={
    "id": venue[0][0].id,
    "name": venue[0][0].name,
    "genres": genres_list,
    "city": venue[0][0].city,
    "state": venue[0][0].state,
    "phone": venue[0][0].phone,
    "website": venue[0][0].website_link,
    "facebook_link": venue[0][0].facebook_link,
    "seeking_talent": venue[0][0].seeking_talent,
    "seeking_description": venue[0][0].seeking_description,
    "image_link": venue[0][0].image_link,
    "past_shows": past_show,
    "upcoming_shows": upcoming_show,
    "past_shows_count": len(past_show),
    "upcoming_shows_count": len(upcoming_show)
  }
  
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm()
  error = false
  # data = VenueForm()
  # TODO: insert form data as a new Venue record in the db, instead
  try:
    venue = Venue(
    name = request.form['name'],
    city = request.form['city'],
    state = request.form['state'], 
    address = request.form['address'],
    phone = request.form['phone'],
    image_link = request.form['image_link'],
    facebook_link = request.form['facebook_link'],
    # genre = request.form['genres'],
    genre = form.genres.data,  
    website_link = request.form['website_link'],
    # seeking_talent = request.form['seeking_talent'],
    seeking_talent = form.seeking_talent.data,
    seeking_description = request.form['seeking_description']
    )
    db.session.add(venue)
    db.session.commit()
  except:
    error = true
    print(sys.exc_info())
    db.session.rollback()
  finally: 
    db.session.close()
  # TODO: modify data to be the data object returned from db insertion
  # on successful db insert, flash success
  if error == false:
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
  else:
      flash('An error occurred. Venue ' + form.name.data + ' could not be listed.')

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artist = db.session.query(Artist.id,Artist.name).all()
  data = artist

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  name = request.form['search_term']
  artists = Artist.query.filter(Artist.name.ilike("%"+name+"%")).all()
  count = 0
  data = []
  response ={}
  for artist in artists:
    data_dict = {
        "id":artist.id,
        "name":artist.name,
        "num_upcoming_shows":0
                 }
    data.append(data_dict)
    count += 1

  response={
    "count": count,
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  # artist = Artist.query.filter_by(id=artist_id ).all()
  # artist = Artist.query.get(artist_id)
  # shows = Show.query.filter_by(artist_id=artist_id ).all()
  artist = db.session.query(Artist,Show).outerjoin(Show).filter(Artist.id == artist_id).all()
  print("***************************************")
  print(artist)
  
  past_show = []
  upcoming_show = []
  # format up comming show and past show 
  if artist[0][1]:
    for _,show in artist:
      venue = Venue.query.get(show.venue_id)
      if show.start_time  < datetime.now():
        p_show = {
          "venue_id": show.venue_id,
          "venue_name": venue.name,
          "venue_image_link": venue.image_link,
          "start_time": str(show.start_time)}
        past_show.append(p_show)
      else:
        u_show = {
          "venue_id": show.venue_id,
          "venue_name": venue.name,
          "venue_image_link": venue.image_link,
          "start_time": str(show.start_time)}
        upcoming_show.append(u_show)
  # format genres to convert it to list
  x1 = artist[0][0].genres[1:-1]
  x1 = str(x1)
  x1 = x1.split(',')
  genres_list = x1

  data={
    "id": artist[0][0].id,
    "name": artist[0][0].name,
    "genres": genres_list,
    "city": artist[0][0].city,
    "state": artist[0][0].state,
    "phone": artist[0][0].phone,
    "website": artist[0][0].website_link,
    "facebook_link": artist[0][0].facebook_link,
    "seeking_venue": artist[0][0].seeking_venue,
    "seeking_description": artist[0][0].seeking_description,
    "image_link": artist[0][0].image_link,
    "past_shows": past_show,
    "upcoming_shows": upcoming_show,
    "past_shows_count": len(past_show),
    "upcoming_shows_count": len(upcoming_show)
  }
  
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
    # format genres to convert it to list
  x1 = artist.genres[1:-1]
  x1 = str(x1)
  x1 = x1.split(',')
  genres_list = x1

  data={
    "id": artist.id,
    "name": artist.name,
    "genres": genres_list,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link
  }

  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=data)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  
  artist.name = form.name.data,
  artist.city = form.city.data,
  artist.state = form.state.data,     
  artist.phone = form.phone.data,
  artist.image_link = form.image_link.data,
  artist.facebook_link = form.facebook_link.data,
  artist.genres = form.genres.data,
  artist.website_link = form.website_link.data,
  artist.seeking_description = form.seeking_description.data
  artist.seeking_venue = form.seeking_venue.data
  
  db.session.commit()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  
  
  x1 = venue.genre[1:-1]
  x1 = str(x1)
  x1 = x1.split(',')
  genres_list = x1

  
  data={
    "id": venue.id,
    "name": venue.name,
    "genres": genres_list,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
  }

  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=data)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form = VenueForm()
  venue = Venue.query.get(venue_id)
    
  venue.name = form.name.data,
  venue.city = form.city.data,
  venue.state = form.state.data,     
  venue.phone = form.phone.data,
  venue.image_link = form.image_link.data,
  venue.facebook_link = form.facebook_link.data,
  venue.genre = form.genres.data,
  venue.website_link = form.website_link.data,
  venue.seeking_description = form.seeking_description.data
  venue.seeking_talent = form.seeking_talent.data
  
  db.session.commit()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  form = ArtistForm()
  error = false
  try:
    artist = Artist(
      name = form.name.data,
      city = form.city.data,
      state = form.state.data,
      
      phone = form.phone.data,
      image_link = form.image_link.data,
      facebook_link = form.facebook_link.data,
      genres = form.genres.data,
      website_link = form.website_link.data,
      seeking_venue = form.seeking_venue.data,
      seeking_description = form.seeking_description.data

    )
    db.session.add(artist)
    db.session.commit()
  except:
    error = true
    print(sys.exc_info())
    db.session.rollback()
  finally: 
    db.session.close()
  # TODO: modify data to be the data object returned from db insertion
  # on successful db insert, flash success
  if error == false:
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
  else:
      flash('An error occurred. Artist ' + form.name.data + ' could not be listed.')

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  shows = Show.query.all()
  data_dict = {}
  data = []
  for show in shows:
    artist = Artist.query.get(show.artist_id)
    venue = Venue.query.get(show.venue_id)
    data_dict = {
      "venue_id": show.venue_id,
      "venue_name": venue.name,
      "artist_id": show.artist_id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": str(show.start_time)
    }
    data.append(data_dict)


  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  
  form = ShowForm()
  error = false
  try:
    show = Show(
      venue_id = form.venue_id.data,
      artist_id = form.artist_id.data,
      start_time = form.start_time.data
    )
    db.session.add(show)
    db.session.commit()
  except:
    error = true
    print(sys.exc_info())
    db.session.rollback()
  finally: 
    db.session.close()
    
  if error == false:
      flash('Show was successfully listed!')
  else:
      flash('An error occurred. Show could not be listed.')

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
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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
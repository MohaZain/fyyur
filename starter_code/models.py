from app import db
from sqlalchemy.orm import relationship

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
    # new columns 
    genre = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120))
    # Relation with Artists 
    artists = relationship("Artist",secondary="show")
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

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
    # new columns 
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120))
    # Relation with Artists 
    venues = relationship("Venue",secondary="show")
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
    __tablename__ = 'show'
    
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'))
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'))
    start_time = db.Column(db.DateTime, nullable=False)
    
    
    
#     # shows the venue page with the given venue_id
#   # TODO: replace with real venue data from the venues table, using venue_id
#   venue = Venue.query.get(venue_id)
#   shows = Show.query.filter_by(venue_id=venue_id).all()
#   # using join to show venues
#   # shows = Venue.query.get(venue_id).join(Venue.Show)
#   past_show = []
#   upcoming_show = []
#   # format up comming show and past show 
#   for show in shows:
#     artist = Artist.query.get(show.artist_id)
#     if show.start_time  < datetime.now():
#       p_show = {
#         "artist_id": show.artist_id,
#         "artist_name": artist.name,
#         "artist_image_link": artist.image_link,
#         "start_time": str(show.start_time)}
#       past_show.append(p_show)
#     else:
#       u_show = {
#         "artist_id": show.artist_id,
#         "artist_name": artist.name,
#         "artist_image_link": artist.image_link,
#         "start_time": str(show.start_time)}
#       upcoming_show.append(u_show)
#   # format genres to convert it to list
#   x1 = venue.genre[1:-1]
#   x1 = str(x1)
#   x1 = x1.split(',')
#   genres_list = x1

#   data={
#     "id": venue.id,
#     "name": venue.name,
#     "genres": genres_list,
#     "city": venue.city,
#     "state": venue.state,
#     "phone": venue.phone,
#     "website": venue.website_link,
#     "facebook_link": venue.facebook_link,
#     "seeking_talent": venue.seeking_talent,
#     "seeking_description": venue.seeking_description,
#     "image_link": venue.image_link,
#     "past_shows": past_show,
#     "upcoming_shows": upcoming_show,
#     "past_shows_count": len(past_show),
#     "upcoming_shows_count": len(upcoming_show)
#   }
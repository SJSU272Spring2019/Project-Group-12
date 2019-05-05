from flask import Flask
from flask_sqlalchemy import SQLAlchemy 
import json
from settings import app

db = SQLAlchemy(app)

locations = []

class CurrentLocation(db.Model):
	__tablename__ = 'current_location'
	id = db.Column(db.Integer, primary_key = True)
	day = db.Column(db.Float, nullable = False)
	hour = db.Column(db.Float, nullable = False)
	latitude = db.Column(db.Float, nullable = False)
	longitude = db.Column(db.Float, nullable = False)

	def json(self):
		return{'day': self.day, 'hour': self.hour, 'latitude': self.latitude, 'longitude': self.longitude}

	def __repr__(self):
		current_location_object = {
			'day':self.day,
			'hour':self.hour,
			'latitude':self.latitude,
			'longitude':self.longitude
		}
		return json.dumps(current_location_object)

	def __init__(self, day, hour, latitude,longitude):
	   self.day = day
	   self.hour = hour
	   self.latitude = latitude
	   self.longitude = longitude
	   locations.append(self)

	def delete_current_parameters(_day,_hour,_latitude,_longitude):
		is_susccessful = CurrentLocation.query.filter_by(day=_day,hour=_hour, latitude=_latitude,longitude=_longitude).delete()
		db.session.commit()
		return bool(is_susccessful)


	def add_current_location_parameters(_day, _hour, _latitude, _longitude):
		new_location = CurrentLocation(day = _day, hour = _hour, latitude = _latitude, longitude = _longitude)
		db.session.add(new_location)
		db.session.commit()

	def get_all_parameters():
		return [CurrentLocation.json(location) for location in CurrentLocation.query.all()]
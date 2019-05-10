from flask import Flask, jsonify, request, Response, render_template, url_for, redirect
import numpy as np
import sys
import json
import tensorflow as tf
import requests
import re
from flask_googlemaps import GoogleMaps
from flask_googlemaps import Map

app = Flask(__name__, template_folder=".")
GoogleMaps(app, key="AIzaSyCXErb05dCXKJWDOHHqK4eUyqLKL6Af7kU")

#enter your username

from settings import *
from CurrentLocation import *

locations = []
locations = [ {"day": "Monday", "hour": "00:00:00", "latitude": "37.349428", "longitude": "-121.905195", "probability": 31.2},
{"day": "Tuesday", "hour": "12:00:00", "latitude": "37.338345", "longitude": "-121.880882", "probability": 39.26}, 
{"day": "Sunday", "hour": "01:00:00", "latitude": "37.331386", "longitude": "-121.883021", "probability": 69.58}, 
{"day": "Wednesday", "hour": "16:00:00", "latitude": "37.332566", "longitude": "-121.885002", "probability": 47.99}, 
{"day": "Thursday", "hour": "15:00:00", "latitude": "37.333202", "longitude": "-121.890130", "probability": 60.47}, 
{"day": "Friday", "hour": "19:00:00", "latitude": "37.330216", "longitude": "-121.887609", "probability": 70.45}, 
{"day": "Saturday", "hour": "18:00:00", "latitude": "37.349428", "longitude": "-121.905195", "probability": 70.72}] 


# Change this value for your machine. The path must match the models folder.
#username = 'renfigue'
#sys.path.append('/Users/'+username+'/Documents/GitHub/Project-Group-12/Models')
sys.path.append('/prog/GitHub/group12v2/Project-Group-12/Models')

import model_v2

#let's load the testing data
#make sure there is a set of data saved under the API directory
testing = model_v2.load_testing_data()

@app.route("/", methods=["GET", "POST"])
@app.route("/index.html", methods=["GET", "POST"])
def about_index():
	return render_template("index.html", locations=locations)

#maps page
@app.route("/advanced_table.html", methods=["GET", "POST"])
def car_break_ins_page():
	if request.method == "POST":
		_day = request.form.get("day", "")
		_hour= request.form.get("hour", "")
		_latitude = request.form.get("latitude", "")
		_longitude = request.form.get("longitude", "")
		print(_day)
		print(type(_day))
		# TO DOS
		# 1. NEED TO FIGURE OUT HOW TO CALL THE PROBABILITY END POINT 
		#http://127.0.0.1:5000/probability?day=0&hour=23&latitude=37.410740&longitude=-121.953370
		# 2. ONCE PROBABILITY IS OBTAINED UPDATE THE FRONT END
		# 3. INTEGRATE GOOGLE MAPS
		number_day = determine_day(_day)
		hour_in_time = format_time(_hour)
		#get probability for yes
		response = requests.get("http://127.0.0.1:5000/probability?day="+number_day+"&hour="+hour_in_time+"&latitude="+_latitude+"&longitude="+_longitude).json()
		#response = requests.get("http://127.0.0.1:5000/probability?day=0&hour=23&latitude=37.410740&longitude=-121.953370").json()
		_probability = response
		_pro_yes = _probability['YES']
		_pro_yes = round(_pro_yes,2)
		new_location = CurrentLocation(day=_day, hour=_hour, latitude=_latitude, longitude=_longitude, probability=_pro_yes)
		locations.append(new_location)

		return redirect(url_for("car_break_ins_page"))
		
	return render_template("advanced_table.html", locations=locations)


#root directory returns all parameters for last location in testing data
@app.route('/current_locations')
def get_all_parameters():
	return jsonify({'Current_Locations':CurrentLocation.get_all_parameters()})


#table page
@app.route("/google_maps.html", methods=["GET", "POST"])
def about_page3():
	# creating a map in the view    
	return render_template("google_maps.html",locations=locations)



#checks the parameters are ok
def validCurrentParameters(parametersObject):
	#check if the parameters contain valid data
	if ("day" in parametersObject 
		and "hour" in parametersObject
		 and "latitude" in parametersObject
		  and "longitude" in parametersObject):
		return True
	else:
		return False

@app.route('/probability')
#sample call 
#http://127.0.0.1:5000/probability?day=0&hour=23&latitude=37.410740&longitude=-121.953370
def get_probability():
	day = request.args.get('day', None)
	hour = request.args.get('hour', None)
	latitude = request.args.get('latitude', None)
	longitude = request.args.get('longitude', None)
	parameters = [day,hour,latitude,longitude]
	model = tf.keras.models.load_model('Final_ML_Model')
	probability = model_v2.get_current_location_probability(model, parameters, testing)
	#add to database
	#convert from numpy.float32 to a float 
	no_car_break = float(probability[0])*100
	car_break = float(probability[1])*100
	CurrentLocation.add_current_location_parameters(day,hour,latitude,longitude, car_break)
	result = {'NO': no_car_break, 'YES': car_break}
	return jsonify(result)

#http://127.0.0.1:5000/current_location?day=0&hour=23&latitude=37.41074&longitude=-121.95337
@app.route('/delete', methods=['DELETE'])
def delete_current_location():
	return jsonify({'Current_Locations':CurrentLocation.clear_data_base()})

def determine_day(day_string):
	day_string = day_string.lower()
	if day_string == "monday":
		return "0"
	elif day_string == "tuesday":
		return "1"
	elif day_string == "wednesday":
		return "2"
	elif day_string == "thursday":
		return "3"
	elif day_string == "friday":
		return "4"
	elif day_string == "saturday":
		return "5"
	elif day_string == "sunday":
		return "6"

def format_time(time):
	match = re.search('(\d{2}|\d{1}):(\d{2}):(\d{2})', time)
	return match.group(1)

if __name__ == "__main__":
	app.run(debug=True, use_reloader=True)

app.run(port=5000)
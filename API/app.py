from flask import Flask, jsonify, request
import numpy as np
import sys
import json
import tensorflow as tf
#enter your username
username = 'renfigue'
sys.path.append('/Users/'+username+'/Documents/GitHub/Project-Group-12/Models')

import model_v2

#let's load the testing data
#make sure there is a set of data saved under the API directory
testing = model_v2.load_testing_data()

app = Flask(__name__)
print(__name__)

#root directory returns all parameters for last location in testing data
@app.route('/')
def get_all_parameters():
	last_parameters = testing[-1]
	day = last_parameters[0]
	hour = last_parameters[1]
	lat = last_parameters[2]
	log = last_parameters[3]
	parameters = {'Day': day, 'Hour': hour, 'Latitude': lat, 'Longitude': log}
	return jsonify(parameters)

#by default this is a GET request
@app.route('/last_coordinates')
def get_coordinates():
	last_parameters = testing[-1]
	lat = last_parameters[2]
	log = last_parameters[3]

	current_location = {'Latitude': lat, 'Longitude': log}
	return jsonify(current_location)

@app.route('/day_of_incident')
def get_day():
	last_parameters = testing[-1]
	day = last_parameters[0]
	day = {'Day': day,}
	return jsonify(day)

@app.route('/hour_of_incident')
def get_hour():
	last_parameters = testing[-1]
	hour = last_parameters[0]
	hour = {'Hour': hour,}
	return jsonify(hour)

# POST /current_parameters
# User will send this as a json object

# {
# 	"day": 0 ,
#  	"hour": 12,
#  	"latitude": 37.434243,
#  	"longitude": -121.24232
# }

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


@app.route('/current_parameters', methods=['POST'])
def add_current_parameters():
	#first get the data from client
	request_data = request.get_json()
	if(validCurrentParameters(request_data)):
		#convert the values from request_data to list
		
		request_data_list = list(request_data.values())
		testing = np.append(testing, [request_data_list], axis = 0)
		return "True"
	else:
		return "False"

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
	#convert from numpy.float32 to a float 
	no_car_break = float(probability[0])*100
	car_break = float(probability[1])*100
	result = {'NO': no_car_break, 'YES': car_break}
	return jsonify(result)
	#return jsonify({'Day':day, "Hour":hour, "Latitude":latitude, "Longitude":longitude})

app.run(port=5000)
from flask import Flask, jsonify, request, Response 
import numpy as np
import sys
import json
import tensorflow as tf
#enter your username

from settings import *
from CurrentLocation import *

username = 'renfigue'
sys.path.append('/Users/'+username+'/Documents/GitHub/Project-Group-12/Models')

import model_v2

#let's load the testing data
#make sure there is a set of data saved under the API directory
testing = model_v2.load_testing_data()



#root directory returns all parameters for last location in testing data
@app.route('/current_locations')
def get_all_parameters():
	return jsonify({'Current_Locations':CurrentLocation.get_all_parameters()})


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

# POST /current_parameters
# User will send this as a json object

# {
# 	"day": 0 ,
#  	"hour": 12,
#  	"latitude": 37.434243,
#  	"longitude": -121.24232
# }

@app.route('/current_parameters', methods=['POST'])
def add_current_parameters():
	#first get the data from client
	request_data = request.get_json()
	if(validCurrentParameters(request_data)):
		CurrentLocation.add_current_location_parameters(request_data['day'], request_data['hour'], request_data['latitude'], request_data['longitude'])
		response = Response("",status=201,mimetype='application/json')
		response.headers['Location'] = "/current_location/" + str(request_data['latitude']) + '&' + str(request_data['longitude'])
		return response
	else:
		invalidCurrentLocationErrorMsg = {
		"error": "Invalid current location, day or time passed in request",
		}
		response  = Response(json.dumps(invalidCurrentLocationErrorMsg), status=400, mimetype='application/json')
		return response

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
	CurrentLocation.add_current_location_parameters(day,hour,latitude,longitude)
	#convert from numpy.float32 to a float 
	no_car_break = float(probability[0])*100
	car_break = float(probability[1])*100
	result = {'NO': no_car_break, 'YES': car_break}
	return jsonify(result)

#http://127.0.0.1:5000/current_location?day=0&hour=23&latitude=37.41074&longitude=-121.95337
@app.route('/current_location', methods=['DELETE'])
def delete_current_location():
	day = request.args.get('day', None)
	hour = request.args.get('hour', None)
	latitude = request.args.get('latitude', None)
	longitude = request.args.get('longitude', None)
	if(CurrentLocation.delete_current_parameters(day,hour,latitude,longitude)):
		response = Response("", status=204)
		return response
	invalidCurrentLocationErrorMsg = {
		"error": "Current location provided not found, so unable to delete."
	}
	response = Response(json.dumps(invalidCurrentLocationErrorMsg), status=404, mimetype='application/json')
	return response



app.run(port=5000)
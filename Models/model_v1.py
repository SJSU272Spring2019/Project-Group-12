# Initial ML model 

# Rene Figueroa 4/19/2019

# Helper libraries
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from load_data import get_data
from sklearn.preprocessing import MinMaxScaler


#import tensor flow and TensorFlow Datasets
import tensorflow as tf

tf.logging.set_verbosity(tf.logging.ERROR)

# The crime_data argument is the data obtained from moto.data.socrata.com
# it pre process the data for the machine learning to be trained. 
# it returns the scaled training and testing data along with its corressponding labels as numpy arrays


def pre_process_data(crime_data):
    vehicle_break_ins = crime_data[crime_data.incident_type_primary == "VEHICLE BURGLARY"]
# There are records from 11/09/2017 until 02/18/2019
# For our initial model, we are only interested in the location as latitude and longitude.
#First we need to preprocess the data for our ML model 
#we will refer to the no car burglary from the data as no_vehicle_break_ins
    no_vehicle_break_ins = crime_data[0:1000]
# merge the no_vehicle_break_ins and the vehicle_break_ins together.
    sample_data = pd.concat([vehicle_break_ins, no_vehicle_break_ins], ignore_index = True)
#randomize the order and reset index
    sample_data = sample_data.sample(frac = 1).reset_index(drop=True)
#need to add a numerical value of 1 (true) to 'Theft from Vehicle' and 0 (false) to anything else under the parent_incident_type column
    sample_data = sample_data.replace('Theft from Vehicle', 1)
#Replace everything else with a 0
    sample_data = sample_data.replace({'parent_incident_type': '[A-Za-z]'},0,regex = True)

#Remove data that will not be used for initial model
    sample_data.pop('incident_id')
    sample_data.pop('case_number')
    sample_data.pop('incident_datetime')
    sample_data.pop('incident_type_primary')
    sample_data.pop('incident_description')
    sample_data.pop('clearance_type')
    sample_data.pop('address_1')
#sample_data.pop('address_2') Not included when called with the api
    sample_data.pop('city')
    sample_data.pop('state')
    sample_data.pop('zip')
#sample_data.pop('country') Not included when called with the api
    sample_data.pop('created_at')
    sample_data.pop('updated_at')
    sample_data.pop('location')
    sample_data.pop('hour_of_day')
    sample_data.pop('day_of_week')

#Training data set will be 80% and testing data will be 20%.

    training_data = sample_data[0:math.ceil(len(sample_data)*0.8)]
    testing_data = sample_data[len(training_data):len(sample_data)]

    training_data_labels = training_data.pop("parent_incident_type")
    testing_data_labels = testing_data.pop("parent_incident_type")

#Since Keras takes the input information as np arrays, we need to convert the data frame to such data structure.

    training_data = np.array(training_data)
    testing_data = np.array(testing_data)
    training_data_labels = np.array(training_data_labels)
    testing_data_labels = np.array(testing_data_labels)

#the final step in preprocessing the training and testing data is to normalize between 0 and 1.

    scaler = MinMaxScaler(feature_range=(0,1))
    scaled_training_samples = scaler.fit_transform(training_data)
    scaled_testing_samples = scaler.fit_transform(testing_data)
    #return the training and testing data along with their labels
    return scaled_training_samples, scaled_testing_samples, training_data_labels, testing_data_labels

# This function builds the machine learning model.
# the arguments are training data with its labels and test_data with its test labels 
# we also print the accuracy of our model
# the function returns the machine learning model


def build_ml_model(train_data, train_labels, test_data, test_labels):
    model = tf.keras.Sequential([
    #only first layer of the sequential model needs to know the shape of the input data
    tf.keras.layers.Dense(16,input_shape=[2], activation=tf.nn.relu),
    #second layer 
    tf.keras.layers.Dense(32, activation=tf.nn.relu),
    #last layer is the output layer, we only have 2 units for car burglary or no car burglary
    tf.keras.layers.Dense(2, activation=tf.nn.softmax)
    ])

    model.compile(optimizer='adam',
              loss = 'sparse_categorical_crossentropy',
              metrics = ['accuracy'])

    model.fit(train_data, train_labels, batch_size = 10, epochs = 20, shuffle = True, verbose =2)

    test_loss, test_acc = model.evaluate(test_data, test_labels)
    #print the accuracy
    print('Test accuracy:', test_acc)
    #return the ML model
    return model

# The crime_data argument is the data obtained from moto.data.socrata.com
# it returns the train and test data (latitude and longitude) without being scaled.
# we need the testing data to scaled the user's location

def get_test_and_train_data(crime_data):
    vehicle_break_ins = crime_data[(crime_data.incident_type_primary == "VEHICLE BURGLARY")]
    no_vehicle_break_ins = crime_data[0:1000]
    sample_data = pd.concat([vehicle_break_ins, no_vehicle_break_ins], ignore_index = True)
    sample_data = sample_data.sample(frac = 1).reset_index(drop=True)
    sample_data = sample_data.replace('Theft from Vehicle', 1)
    sample_data = sample_data.replace({'parent_incident_type': '[A-Za-z]'},0,regex = True)
    sample_data.pop('incident_id')
    sample_data.pop('case_number')
    sample_data.pop('incident_datetime')
    sample_data.pop('incident_type_primary')
    sample_data.pop('incident_description')
    sample_data.pop('clearance_type')
    sample_data.pop('address_1')
    sample_data.pop('city')
    sample_data.pop('state')
    sample_data.pop('zip')
    sample_data.pop('created_at')
    sample_data.pop('updated_at')
    sample_data.pop('location')
    sample_data.pop('hour_of_day')
    sample_data.pop('day_of_week')
    training_data = sample_data[0:math.ceil(len(sample_data)*0.8)]
    testing_data = sample_data[len(training_data):len(sample_data)]
    #remove the "parent_incident_type"
    training_data.pop("parent_incident_type")
    testing_data.pop("parent_incident_type")
    return np.array(training_data), np.array(testing_data)




#model is the machine learning model being used
#current_location is a numpy array with the latitude and longitude in it. 
#testing_data is a numpy array with latitude and longitude without being scaled
#returns a list with the probabilies of car being broken into
# probability at index 0 is for false and index 1 is for true (car broken into)
def get_current_location_probability(model, current_location, testing_data):
    scaler = MinMaxScaler(feature_range=(0,1))
    current_testing_data = np.append(testing_data, [current_location], axis=0)

    #print(current_testing_data) <-- uncomment to see the location added to the testing data set
#scaled the testing data 
    current_testing_data_scaled = scaler.fit_transform(current_testing_data)
#now we have normalized the data and to access the current location we use [-1]

    current_prediction = model.predict(current_testing_data_scaled, batch_size = 10, verbose = 0)
    return list(current_prediction[-1])



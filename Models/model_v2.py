# Final ML model 

# Rene Figueroa 4/23/2019

# Helper libraries
import math
import numpy as np
import pandas as pd

from load_data import get_data
from sklearn.preprocessing import MinMaxScaler


#import tensor flow and TensorFlow Datasets
import tensorflow as tf

tf.logging.set_verbosity(tf.logging.ERROR)

# The crime_data argument is the data obtained from moto.data.socrata.com
# it pre process the data for the machine learning to be trained. 
# it returns the scaled training and testing data along with its corressponding labels as numpy arrays


#create another function to pop the data

#COPY OVER FROM JUPYTER NOTEBOOK
#INCREASE ACCURACY FROM 70% TO 80-85%

#returns the data colums we are interested in keeping:
#day_of_week, hour_of_day, latitude, longitude and parent_incident_type

def remove_uncessary_data(crime_data):
    crime_data.pop('incident_id')
    crime_data.pop('case_number')
    crime_data.pop('incident_datetime')
    crime_data.pop('incident_type_primary')
    crime_data.pop('incident_description')
    crime_data.pop('clearance_type')
    crime_data.pop('address_1')
    crime_data.pop('city')
    crime_data.pop('state')
    crime_data.pop('zip')
    crime_data.pop('created_at')
    crime_data.pop('updated_at')
    crime_data.pop('location')
    return crime_data

#function takes the data as a Pandas frame and cleans the data
#function returns a Pandas frame with features and labels that will be used in the machine learning model. 
#it replaces the string values with numerical values

def clean_data(crime_data):
    vehicle_break_ins = crime_data[crime_data.incident_type_primary == "VEHICLE BURGLARY"]
    no_vehicle_break_ins = crime_data[0:1000]
    sample_data = pd.concat([vehicle_break_ins, no_vehicle_break_ins], ignore_index = True)
    #Randomnize the data
    sample_data = sample_data.sample(frac = 1).reset_index(drop=True)
    #replace the 'Theft from Vehicle' with value 1
    sample_data = sample_data.replace('Theft from Vehicle', 1)
    #replace everything else under the parent_incident_type with a 0
    sample_data = sample_data.replace({'parent_incident_type': '[A-Za-z]'},0,regex = True)
    #remove the unncessary data
    sample_data = remove_uncessary_data(sample_data)
    #replace the days of the week with numerical values
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    days_in_value = [0,1,2,3,4,5,6]
    sample_data['day_of_week'].replace(days,days_in_value, inplace = True)
    # return the clean data as a Pandas data frame
    return sample_data

# function takes the Pandas data frame returned from clean data and feature scales (normalize) the values so the machine learning model can take the data.
# the normalization of data can help speed up the machine learning algorithm.  
# it transform the data frame to numpy arrays and splits the data in features and labels. The data is further split into training and testing data. 
# functio returns the scaled training features, scaled testing features, training labels, and testing labels
def pre_process_data(crime_data):
    #Training data set will be 80% and testing data will be 20%.

    training_data = crime_data[0:math.ceil(len(crime_data)*0.8)]
    testing_data = crime_data[len(training_data):len(crime_data)]

    training_data_labels = training_data.pop("parent_incident_type")
    testing_data_labels = testing_data.pop("parent_incident_type")

#Since Keras takes the input information as np arrays, we need to convert the data frame to such data structure.
#The order for the data in training and testing sets is day_of_week, hour_of_day, latitude, longitude

#[[2 '8' '37.33777289850083' '-122.0131484592137']
 #[2 '17' '37.33713357367402' '-121.88723116390365']

    training_data = np.array(training_data)
    testing_data = np.array(testing_data)

    training_data_labels = np.array(training_data_labels)
    testing_data_labels = np.array(testing_data_labels)

    #convert to float numpy arrays
    training_data = training_data.astype(float)
    testing_data = testing_data.astype(float)
    training_data_labels = training_data_labels.astype(float)
    testing_data_labels = testing_data_labels.astype(float)

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
    #the input data now has 4 values, week_of_day, hour_of_day, latitude, longitude
    tf.keras.layers.Dense(16,input_shape=[4], activation=tf.nn.relu),
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

# function takes the Pandas data frame returned from clean data

def get_unnormalized_train_and_test_data(crime_data):
    training_data = crime_data[0:math.ceil(len(crime_data)*0.8)]
    testing_data = crime_data[len(training_data):len(crime_data)]
    #remove the "parent_incident_type"
    training_data.pop("parent_incident_type")
    testing_data.pop("parent_incident_type")
    return np.array(training_data).astype(float), np.array(testing_data).astype(float)


#model is the machine learning model being used
#current_parameters is a list containing the day_of_week, hour_of_day, latitude and longitude 
#testing_data is an unnormalized numpy array with day_of_week, hour_of_day, latitude and longitude 
#returns a list with the probabilies of car being broken into
# probability at index 0 is for false and index 1 is for true (car broken into)
def get_current_location_probability(model, current_parameters, testing_data):
    
    #first convert the current_parameters to a numpy array
    current_parameters = np.array(current_parameters)
    #then append the user's data to the testing_data
    current_testing_data = np.append(testing_data, [current_parameters], axis=0)

    #now normalize the data
    scaler = MinMaxScaler(feature_range=(0,1))
    current_testing_data_scaled = scaler.fit_transform(current_testing_data)
    print(current_testing_data_scaled )
    current_prediction = model.predict(current_testing_data_scaled, batch_size = 10, verbose = 0)
    #return the prediction
    return current_prediction[-1]

def save_data(filename,data_to_be_saved):
    #save as .npy 
    np.save(filename, data_to_be_saved)




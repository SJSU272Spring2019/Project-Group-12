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
import tensorflow_datasets as tfds
tf.logging.set_verbosity(tf.logging.ERROR)




#Load the crime report data
data = get_data()

#Collect data for "VEHICLE BURGLARY" incidents only
vehicle_break_ins = data[data.incident_type_primary == "VEHICLE BURGLARY"]

# There are records from 11/09/2017 until 02/18/2019
# For our initial model, we are only interested in the location as latitude and longitude.

#First we need to preprocess the data for our ML model 

#we will refer to the no car burglary from the data as no_vehicle_break_ins
no_vehicle_break_ins = data[0:1000]

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
#sample_data.pop('address_2')
sample_data.pop('city')
sample_data.pop('state')
sample_data.pop('zip')
#sample_data.pop('country')
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


#Next, we build the ML model

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

model.fit(scaled_training_samples, training_data_labels, batch_size = 10, epochs = 20, shuffle = True, verbose =2)

test_loss, test_acc = model.evaluate(scaled_testing_samples, testing_data_labels)

print('Test accuracy:', test_acc)


predictions = model.predict(scaled_testing_samples, batch_size = 10, verbose = 0)

#The predictions are given as an array of vectors and the values inside are the probabilities

for i in predictions:
    print(i)
#We can test the prediction against the testing label. For example, prediction[0] predicts that the car would be broken into.

print(predictions[0])
print(testing_data_labels[0])

#We can use the model predict_classes to have the value with the highest probability returned

predictions_probability = model.predict_classes(scaled_testing_samples, batch_size=10, verbose=0)

for i in predictions_probability:
    print(i)

 #we can check against our testing labels 

print(testing_data_labels)

#	TODO 
# SAVE ML MODEL 
# split model into functions/classes?

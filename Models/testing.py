
from load_data import get_data

import model_v2

import tensorflow as tf
 
import numpy as np


#Load the crime report data
#data = get_data()

#file_name = "un_normalized_testing_data2"

testing = np.load("un_normalized_testing_data2.npy")





#data = model_v2.clean_data(data)

#need to store testing data in dabase

#training, testing = model_v2.get_unnormalized_train_and_test_data(data);
#model_v2.save_data(file_name,testing)
# save testing data 
#np.save("unnormalized_testing_data", testing)


#importing saved model. 
new_model = tf.keras.models.load_model('Final_ML_Model')


#test lat and log
lat = 37.410740
log = -121.953370
day = 6
hour = 23
# train, test = get_test_and_train_data(data)

parameters = [day, hour, lat, log]
print(model_v2.get_current_location_probability(new_model, parameters, testing))


# write api to talk to front end
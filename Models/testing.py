from model_v1 import pre_process_data, build_ml_model, get_test_and_train_data, get_current_location_probability
from load_data import get_data
import numpy as np

#Load the crime report data
data = get_data()
training, testing, train_labels, test_labels = pre_process_data(data);



model = build_ml_model(training, train_labels, testing, test_labels)
# save the model
model.save('Location_based_ML_model')

predictions = model.predict(testing, batch_size=10, verbose=0)


 #we can check against our testing labels 


#latitude and longitude for SJSU
lat = 37.332642
log = -121.878677

train, test = get_test_and_train_data(data)

current_location = [lat, log]
current_location = np.array(current_location)

current_probability = get_current_location_probability(model, current_location, test)





print("PROBABILIES")
print(current_probability)
print("Location: ", current_location)

if current_probability[0] > 0.5:
	print("Car not broken into")
	print("Probability: {0:.2f}".format(current_probability[0]*100))
else:
	print("Car broken into")
	print("Probability: {0:.2f}".format(current_probability[1]*100))

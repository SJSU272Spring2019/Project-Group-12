#test API

def validCurrentParameters(parametersObject):
	#check if the parameters contain valid data
	if ("day" in parametersObject 
		and "hour" in parametersObject
		 and "latitude" in parametersObject
		  and "longitude" in parametersObject):
		return True
	else:
		return False

valid_para = {
    "day": 0,
    "hour": 12,
    "latitude": 37.434243,
    "longitude": -121.24232
}

empty = {}


missing_hour = {
    
    "hour": 12,
    "latitude": 37.434243,
    "longitude": -121.24232
}


valid_para = {
    "day": 0,
    "hour": 12,
    "latitude": 37.434243,
    "longitude": -121.24232
}
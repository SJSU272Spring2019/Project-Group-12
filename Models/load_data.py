#loading the data for the ML model 

# Initial ML model 
# make sure to install these packages before running:
# pip install pandas
# pip install sodapy

import pandas as pd
from sodapy import Socrata

# Unauthenticated client only works with public data sets. Note 'None'

# in place of application token, and no username or password:
#client = Socrata("moto.data.socrata.com", None)

# Example authenticated client (needed for non-public datasets):
# client = Socrata(moto.data.socrata.com,
#                  MyAppToken,
#                  userame="user@example.com",
#                  password="AFakePassword")

def get_data():
	# The results are returned as JSON from API / converted to Python list of
# dictionaries by sodapy.
	client = Socrata("moto.data.socrata.com", None)

# We know the size of the data is 138648. If we want no limit, then we use limit=None, but we get the following warning:

#WARNING:root:Requests made without an app_token will be subject to strict throttling limits.
	results = client.get("wrmr-tdyp", limit=138648)
	# Convert to pandas DataFrame
	data = pd.DataFrame.from_records(results)
	return data

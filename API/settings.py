from flask import Flask 

app = Flask(__name__)

#will store the database in the API folder 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///location_parameters.db'
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False 
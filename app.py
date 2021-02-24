import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect, extract

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
# Note: Two tables used for analysis
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """Welcome to the Hawaii Weather API"""
    return (
        f"Available API Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create session from Python to the DB
    session = Session(engine)

    # Query all precipitation data
    results = session.query(Measurement.date, Measurement.prcp).all()

    #POTATO - is this needed here? >> session.close()
    
    precipitation_data = []
    for date, prcp in results:
        precipitation_dict = {}
        precipitation_dict["Date"] = date
        precipitation_dict["Precipitation"] = prcp
        precipitation_data.append(precipitation_dict)  

    return jsonify(precipitation_data)

if __name__ == "__main__": app.run(debug=True)

import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect, extract

from flask import Flask, jsonify
from datetime import datetime, date, time

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
        f"<h2>Welcome to the Hawaii Weather API</h2>"
        f"<h3>Available API Routes</h3><br/>"
        f"<strong>Static</strong><br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"<br/>"
        f"<strong>Dynamic</strong><br/>"
        f"/api/v1.0/<start>(enter start date here)<br/>"
        f"Enter a start date(m-d-yyyy) to return the minimum, maximum, and average temperatures.<br/>"
        f"Example:/api/v1.0/8-17-2017<br/>"
        f"<br/>"
        f"/api/v1.0/<start><end>(enter start and end dates here)<br/>"
        f"Enter a start and end date (m-d-yyyy) separated by an underscore (_) to return the minimum, maximum, and average temperatures.<br/>"
        f"Example:/api/v1.0/8-17-2017_8-23-2017<br/>"
        f"<br/>"
        f"--------------------<br/>"
        f"Dates available for this dataset start at 1/1/2010 and end at 8/23/2017.<br/>"
    )

#--STATIC API ----------------------------------
#------------------------------------------------

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create session from Python to the DB
    session = Session(engine)

    # Query last year of precipitation data
    results = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= "2016-08-24").\
    filter(Measurement.date <= "2017-08-23").all()

    # Put data into a dictionary format
    precipitation_data = []
    for date, prcp in results:
        precipitation_dict = {}
        precipitation_dict["Date"] = date
        precipitation_dict["Precipitation"] = prcp
        precipitation_data.append(precipitation_dict)  

    return jsonify(precipitation_data)

    session.close()

#------------------------------------------------

@app.route("/api/v1.0/stations")
def stations():
    # Create session from Python to the DB
    session = Session(engine)

    # Query all stations in data; use np.ravel to convert to a list
    results = session.query(Station.station).all()
    station_data = list(np.ravel(results))
    
    return jsonify(station_data)

    session.close()

#------------------------------------------------

@app.route("/api/v1.0/tobs")
def tobs():
    # Create session from Python to the DB
    session = Session(engine)

    # Query most active station by observations (tobs) for the last year of data
    results = session.query(Station.station, Measurement.date, Measurement.tobs).\
    filter(Measurement.date >= "2016-08-24").\
    filter(Measurement.date <= "2017-08-23").\
    filter(Station.station == "USC00519281").all()
   
    tobs_data = list(np.ravel(results))
    return jsonify(tobs_data)

    session.close()

#--DYNAMIC API ----------------------------------
#------------------------------------------------

@app.route("/api/v1.0/<start>")
def start_date(start):
    # Create session from Python to the DB
    session = Session(engine)

    # Note: Date input format = 8-5-2017
    start_date = datetime.strptime(start,"%m-%d-%Y").date()
    #start_date = datetime.strptime(start, '%Y-%m-%d').date()

    temp_calc = session.query (func.min (Measurement.tobs), func.max (Measurement.tobs), func.avg (Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()


    # Note: Flatten and put into dictionary format
    temp_results = list(np.ravel(temp_calc))

    min_temp = temp_results[0]
    max_temp = temp_results[1]
    avg_temp = temp_results[2]

    temp_data = []
    temp_dict = [{"Start Date": start_date},
        {"Minimum Temperature for this date": min_temp},
        {"Maximum Temperature for this date": max_temp},
        {"Average Temperature for this date": avg_temp}]

    temp_data.append(temp_dict)

# Note: To simplify code, remove above dictionary code and just use jsonify to display data results.
    return jsonify(temp_dict)

    session.close()

#------------------------------------------------

@app.route("/api/v1.0/<start>_<end>")
def start_end_date(start, end):
    # Create session from Python to the DB
    session = Session(engine)

    # Note: Date input format = 8-5-2017
    start_date = datetime.strptime(start,"%m-%d-%Y").date()
    end_date = datetime.strptime(end,"%m-%d-%Y").date()

    temp_calc = session.query (func.min(Measurement.tobs), func.max (Measurement.tobs), func.avg (Measurement.tobs)).\
        filter(Measurement.date >= start_date).\
        filter(Measurement.date <= end_date).all()
    
    # Note: Flatten and put into dictionary format
    temp_results = list(np.ravel(temp_calc))

    min_temp = temp_results[0]
    max_temp = temp_results[1]
    avg_temp = temp_results[2]

    temp_data = []
    temp_dict = [{"Start Date": start_date},{"End Date": end_date},
        {"Minimum Temperature for this date range": min_temp},
        {"Maximum Temperature for this date range": max_temp},
        {"Average Temperature for this date range": avg_temp}]

    temp_data.append(temp_dict)
    
    # Note: To simplify code, remove above dictionary code and just use jsonify to display data results.
    return jsonify(temp_dict)

    session.close()

#------------------------------------------------

if __name__ == "__main__": app.run(debug=True)

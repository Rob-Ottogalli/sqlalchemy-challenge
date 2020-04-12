import numpy as np

import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

# Define function to convert strings to datetimes
def convert(date_time): 
    format ="%Y-%m-%d" # The format 
    datetime_str = dt.datetime.strptime(date_time, format) 
   
    return datetime_str

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of Dates and Precipitation"""
    
    # Calculate the date 1 year ago from the last data point in the database
    last_date = (session.query(Measurement.date)
                .order_by(Measurement.date.desc()).first())

    # Set variable to hold date of 1 year prior
    year_prior = convert(last_date[0]) - dt.timedelta(days=365)

    # Query Date range
    results = (session.query(Measurement.date, Measurement.prcp)
              .filter(Measurement.date >= year_prior))

    session.close()

    # Create a dictionary from the row data and append to a list of date_prcp
    date_prcp = []
    for date, prcp in results:
        date_prcp_dict = {}
        date_prcp_dict["date"] = date
        date_prcp_dict["prcp"] = prcp
        date_prcp.append(date_prcp_dict)

    return jsonify(date_prcp)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of station names"""

    # Calculate the date 1 year ago from the last data point in the database
    last_date = (session.query(Measurement.date)
                .order_by(Measurement.date.desc()).first())

    # Set variable to hold date of 1 year prior
    year_prior = convert(last_date[0]) - dt.timedelta(days=365)

    # Set a query to list unique stations
    results = (session.query(Measurement.station)
            .filter(Measurement.date >= year_prior)
            .group_by(Measurement.station)
            .order_by(func.count(Measurement.station).desc())
            .all())
    
    session.close()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)

if __name__ == '__main__':
    app.run(debug=True)
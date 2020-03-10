import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify



# Create engine to connect with database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# Reflect an existing database into a new model
Base = automap_base()
# Reflect the tables
Base.prepare(engine, reflect=True)
# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station
# Create session (link)  to the DB
session = Session(engine)

# Flask Setup
app = Flask(__name__)


# Create routes
@app.route("/")
def welcome():
    return """
    Welcome to Climate API for Hawaii!
    Available endpoints: <br>
    /api/v1.0/precipitation <br>
    /api/v1.0/stations <br>
    /api/v1.0/tobs <br>
    /api/v1.0/&lt;start&gt; where start is a date in YYYY-MM-DD format <br> 
    /api/v1.0/&lt;start&gt;/&lt;end&gt; where start and end are dates in YYYY-MM-DD format
    """

@app.route("/api/v1.0/precipitation")

def precipitation():

#retrieve the last 12 months of precipitation data
    precipitation_data = session.query(Measurement.date,Measurement.prcp).order_by(Measurement.date.desc()).all()    
#put the results in a list
    precipitation_dict = []
    for row in precipitation_data:
        date_dict = {}
        date_dict[row.date] = row.prcp
        precipitation_dict.append(date_dict)

    return jsonify(precipitation_dict)


@app.route("/api/v1.0/stations")
def stations():
#retrive the list of stations
    station_data = session.query(Measurement.station,func.count(Measurement.tobs)).group_by(Measurement.station).order_by(func.count(Measurement.tobs).desc()).all()
    
#np.ravel function to put the results in a ist     
    station_list = list(np.ravel(station_data))
    return jsonify(station_list)


@app.route("/api/v1.0/tobs")
def tobs():
    results = session.query(Measurement.tobs).\
        filter(Measurement.date >= "2016-08-23").\
        filter(Measurement.date <= "2017-08-23").all()

    tobs_list = list(np.ravel(results))
    return jsonify(tobs_list)

@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    """Return TMIN, TAVG, TMAX."""

    # Select statement
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        # calculate TMIN, TAVG, TMAX for dates greater than start
        results = session.query(*sel).\
            filter(Measurement.date >= start).all()
        # Unravel results into a 1D array and convert to a list
        temps = list(np.ravel(results))
        return jsonify(temps)

    # calculate TMIN, TAVG, TMAX with start and stop
    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    # Unravel results into a 1D array and convert to a list
    temps = list(np.ravel(results))
    return jsonify(temps)

if __name__ == '__main__':
    app.run(debug=True)

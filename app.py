# Import the dependencies.
from flask import Flask, jsonify
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

#################################################
# Database Setup
#################################################
# reflect an existing database into a new model
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect the tables
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
# set the home route and list available routes
@app.route("/")
def welcome():
    """List all available routes"""
    return (
        f"<strong>Welcome to my Climate App!<br/><br/>"
        f"<u>Available Routes:</u><br/><br/></strong>"
        f"<i>Precipitation analysis</i>: /api/v1.0/precipitation<br/>"
        f"<i>Stations</i>: /api/v1.0/stations<br/>"
        f"<i>Most active station temp</i>: /api/v1.0/tobs<br/>"
        f"<i>Temps from start</i>: /api/v1.0/start<br/>"
        f"<i>Temps for specified start-end</i>: /api/v1.0/start/end<br/>"
    )
# create first date variable for the elements that look into the last 12 months of data
def last_year(): 
    session = Session(engine)
    last_date = session.query(func.max(Measurement.date)).first()[0]
    first_date = dt.datetime.strptime(last_date, "%Y-%m-%d") - dt.timedelta(days=365)
    session.close()
    return(first_date)

# Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data) to a dictionary using date as the key and prcp as the value.
# Return the JSON representation of your dictionary.
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    p_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= last_year()).all()
    session.close()
    # create dictionary to hold the precipitation data and append as you loop
    precip_data = []
    for date, prcp in p_data:
        p_dict = {}
        p_dict[date] = prcp
        precip_data.append(p_dict)
    # jsonify the precipitation dictionary
    return jsonify(precip_data)

# Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    result = session.query(Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation).all()
    session.close()
    # create station dictionary to store each station's name, ID, lat, long, and elevation
    stations = []
    for station, name, latitude, longitude, elevation in result:
        s_dict = {}
        s_dict['station'] = station
        s_dict['name'] = name
        s_dict['latitude'] = latitude
        s_dict['longitude'] = longitude
        s_dict['elevation'] = elevation
        stations.append(s_dict)
    return jsonify(stations)

# Query the dates and temperature observations of the most-active station for the previous year of data.
# Return a JSON list of temperature observations for the previous year.
@app.route("/api/v1.0/tobs")
def tobs():
    #create query to pull the last 12 months of data from USC00519281 (most active station)
    session = Session(engine)
    t_data = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == 'USC00519281').\
                        filter(Measurement.date >= last_year()).all()               
    session.close()
    #create the tobs dictionary for when you loop
    t_list = []
    for date, tobs in t_data:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        t_list.append(tobs_dict)
    return jsonify(t_list)

# Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range.
# For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.
# For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.
@app.route("/api/v1.0/<start>")
def start(start=None):
    session = Session(engine)
    sel=[func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    start_data = session.query(*sel).filter(Measurement.date >= start).all()
    start_list = list(np.ravel(start_data))
    return jsonify(start_list)
    session.close()

@app.route("/api/v1.0/<start>/<end>")
def start_end(start=None, end=None):
    session = Session(engine)
    sel=[func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    range_data = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    range_list = list(np.ravel(range_data))
    return jsonify(range_list)
    session.close()

if __name__ == "__main__":
    app.run(debug=True)
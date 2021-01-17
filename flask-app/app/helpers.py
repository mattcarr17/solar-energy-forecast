from app import app, db
from .models import Energy
import json
import plotly
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
from .forecast import predict

def create_plot(d, forecast=False):
    """Creates Plotly plot to be displayed within flask app

    Parameters
    ----------
    d: Pandas dataframe
        data to plot
    forecast: boolean, optional
        Indicates whether d is a forecast dataframe or not.
        If it is, change column 'yhat' to 'y' for plotting purposes
    
    Returns
    -------
    graphJSON: 
        Plotly scatter plot encoded as JSON object
    """

    df = d.copy()
    if forecast: # if forecast plot, change 'yhat' to 'y'
        df['y'] = df['yhat']

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df['ds'],
            y=df['y']
        )
    )

    fig.update_layout(
        xaxis_title='Time',
        xaxis_title_standoff=0,
        yaxis_title="Energy Production (MWh)",
        height=850,
        width=1300,
        margin=dict(t=20, pad=0)
    )

    # Convert Plotly figure to JSON for plotting with js on front end
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON


def get_recent_data(forecast=False):
    """Queries most recent entries of local postgres database

    This function is utilized by both /historicaldata and /forecast
    endpoints. The parameter 'forecast' denotes which endpoint this
    function is being used for when called. /historicaldata displays
    most recent 24 hours by default and will query last 24 entries from
    database. Prophet model used for /forecast is trained on 2 weeks
    of hourly data and will query last 2 weeks of entires when 
    forecast is passed as true.

    Parameters
    ----------
    forecast: boolean, optional
        indicates if function is being called for use by 
        /historicaldata or /forecast endpoint

    Returns
    -------
    df: Pandas DataFrame
        contains data from query. Last 24
        hours if forecast=False, last 2 weeks of hourly entries
        if forecast=True
    """

    today = datetime.today()
    if forecast:
        index = today - timedelta(days=14)
    else:
        index= today - timedelta(days=1)

    # filter for query
    start_date = pd.Timestamp(index.year, index.month, index.day, 0, 0, 0)

    # query all dates greater than or equal to start_date
    q = Energy.query.filter(Energy.time >= start_date).all()


    dates = []
    energy_values = []
    for d in q: # extract datetime and corresponding energy production for each row in query
        dates.append(pd.to_datetime(d.time))
        energy_values.append(d.energy)

    # list of tuples to with datetime and corresponding energy to create dataframe
    data = [(t, e) for t, e in zip(dates, energy_values)]
    
    df = pd.DataFrame(columns=['ds', 'y'], data=data)

    return df

def create_forecast():
    """ Creates 24 hour forecast using Prophet

    This function does bulk of work for /forecast endpoint.
    It first queries 2 weeks of data to train model using 'get_recent_data',
    it then trains model in forecast module using this data and get's 24 hour
    forecast using same module. Create's plot of 24 hour forecast with 
    'create_plot' and format's forecast results to be displayed in table
    on forecast page.

    Returns
    -------
    plot: 
        Plotly scatter plot of 24 hour forecast
    formatted_results: list
        Contains forecast for each corresponding hourly timestamp
    date: str
        Date forecast is predicting for

    """

    data = get_recent_data(forecast=True) # get training data

    # train model on new data and make forecast for 24 hours
    results = predict(data)

    plot = create_plot(results, forecast=True)

    # Extract date of forecast
    date = results.values[0][0].strftime("%m/%d/%Y")

    # Format results to display in table on forecast page
    formatted_results = []
    for r in results.values:
        time = datetime.strftime(r[0], '%H:%M:%S')
        energy = round(r[1], 2)
        formatted_results.append((time, energy))
        
    return (plot, formatted_results, date)



from app import app, db
from .models import Energy
import json
import plotly
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
from .forecast import forecast


def create_historical_plot(start_date, end_date, frequency='H'):

    df = create_historical_df(start_date, end_date, frequency)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['energy']
        )
    )

    fig.update_layout(
        xaxis_title="Time",
        yaxis_title="Energy Production (MWh)",
        height=900,
        width=1300
    )

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON

def create_historical_df(start_date, end_date, frequency):
    data_query = Energy.query.with_entities(Energy.time, Energy.energy).\
        filter(Energy.time >= start_date).filter(Energy.time < end_date).all()
    
    dates = []
    energy_values = []
    for d in data_query:
        dates.append(d[0])
        energy_values.append(d[1])

    df = pd.DataFrame(index=pd.to_datetime(dates), columns=['energy'], data=energy_values)
    df_resampled = df.resample(frequency).sum()

    return df_resampled

def create_forecast():
    data = get_training_data()
    results = forecast(data)
    plot = forecast_plot(results)
    formatted_results = []
    for r in results.values:
        time = datetime.strftime(r[0], '%H:%M:%S')
        energy = round(r[1], 2)
        formatted_results.append((time, energy))
    return (plot, formatted_results)

def get_training_data():
    today2 = datetime.today()
    index = today2 - timedelta(days=14)
    start_date2 = pd.Timestamp(index.year, index.month, index.day, 0, 0, 0)

    q = Energy.query.filter(Energy.time >= start_date2).all()

    dates = []
    energy_values = []
    for d in q:
        dates.append(pd.to_datetime(d.time))
        energy_values.append(d.energy)

    data = [(t, e) for t, e in zip(dates, energy_values)]
    
    df = pd.DataFrame(columns=['ds', 'y'], data=data)
    return df

def forecast_plot(d):
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=d['ds'],
            y=d['yhat']
        )
    )

    fig.update_layout(
        xaxis_title="Time",
        yaxis_title="Energy Production (MWh)",
        height=900,
        width=1300
    )

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON
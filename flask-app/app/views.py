from flask import Blueprint, render_template, request
from app import app, db
from .models import Energy
import plotly
import plotly.graph_objects as go
import json
import pandas as pd
from datetime import datetime, timedelta

views = Blueprint('views', __name__, template_folder='templates', static_folder='static')

@views.route('/')
def index():
    return render_template('index.html')


@views.route('/historicaldata', methods=['GET', 'POST'])
def historical_plot():
    if request.method == 'POST':
        start_date = pd.Timestamp(request.form['start-date'])
        end_date = pd.Timestamp(request.form['end-date'])
        frequency = request.form.get('frequency')
    else:
        today = datetime.today()
        yesterday = today - timedelta(days=1)
        start_date = pd.Timestamp(yesterday.year, yesterday.month, yesterday.day, 0, 0, 0)
        end_date = pd.Timestamp(today.year, today.month, today.day, 0, 0, 0)
        frequency = 'H'

    frequency_dict = {'H': 'Hourly', 'D': 'Daily', 'W': 'Weekly', 'M': 'Monthly'}
    
    plot = create_historical_plot(start_date, end_date, frequency)
    dates = [start_date.strftime("%m/%d/%Y"), end_date.strftime("%m/%d/%Y")]

    return render_template('historical_data.html', dates=dates, frequency=frequency_dict[frequency], plot=plot)

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
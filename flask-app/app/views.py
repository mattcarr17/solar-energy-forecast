from flask import Blueprint, render_template, request
import pandas as pd
from datetime import datetime, timedelta
from .helpers import *
from .models import Energy


# Create views blueprint to endpoints to app/
views = Blueprint('views', __name__, template_folder='templates', static_folder='static')


# Home page endpoint
@views.route('/')
def index():
    return render_template('pages/index.html')


# Historical Data page endpoint
@views.route('/historicaldata', methods=['GET', 'POST'])
def historical_plot():
    if request.method == 'POST':
        start_date = pd.Timestamp(request.form['start-date'])
        end_date = pd.Timestamp(request.form['end-date'])
        frequency = request.form.get('frequency')
        data_query = Energy.query.with_entities(Energy.time, Energy.energy).\
            filter(Energy.time >= start_date).filter(Energy.time < end_date).all()
    
        dates = []
        energy_values = []
        for d in data_query:
            dates.append(d[0])
            energy_values.append(d[1])

        base_df = pd.DataFrame(index=dates, columns=['y'], data=energy_values)
        df = base_df.resample(frequency).sum()
        df['ds'] = df.index
    else:
        df = get_recent_data()
        frequency = 'H'

    frequency_dict = {'H': 'Hourly', 'D': 'Daily', 'W': 'Weekly', 'M': 'Monthly'}
    
    plot = create_plot(df)
    times = [pd.Timestamp(t) for t in df['ds'].values]
    dates = [times[0].strftime("%m/%d/%Y"), times[-1].strftime("%m/%d/%Y")]

    return render_template('pages/historical_data.html', dates=dates, frequency=frequency_dict[frequency], plot=plot)


# Forecast page endpoint
@views.route('/forecasts')
def display_forecast():
    results = create_forecast()
    return render_template('pages/forecasts.html', plot=results[0], results=results[1], date=results[2])

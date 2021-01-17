from flask import Blueprint, render_template, request
import pandas as pd
from datetime import datetime, timedelta
from .forecast import forecast
from .utils import *

views = Blueprint('views', __name__, template_folder='templates', static_folder='static')

@views.route('/')
def index():
    return render_template('pages/index.html')


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

    return render_template('pages/historical_data.html', dates=dates, frequency=frequency_dict[frequency], plot=plot)


@views.route('/forecasts')
def display_forecast():
    results = create_forecast()
    return render_template('pages/forecasts.html', plot=results[0], results=results[1], date=results[2])

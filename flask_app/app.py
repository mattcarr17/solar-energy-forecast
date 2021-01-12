import os
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
import plotly
import plotly.graph_objects as go
import json
import pandas as pd
import requests

app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('config.py')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
API_KEY = app.config['API_KEY']
db = SQLAlchemy(app)
migrate = Migrate(app, db)
scheduler = BackgroundScheduler()

def scheduled_db_update():
    error = False
    data = gather_data_from_api()
    try:
        db.session.add_all(data)
        db.session.commit()
    except:
        db.session.rollback()
        error = True
    finally:
        db.session.close()


def gather_data_from_api():
    url = 'http://api.eia.gov/series/?api_key={}&series_id=EBA.MISO-ALL.NG.SUN.H&num=24'.format(API_KEY)
    resp = requests.get(url)
    data = resp.json()
    df = pd.DataFrame(columns=['time', 'energy'], data=data['series'][0]['data'])
    df['time'] = pd.to_datetime(df['time'], utc=True).dt.tz_localize(None)
    time_converter = lambda t: t - timedelta(hours=6)
    df['time'] = df['time'].apply(time_converter)
    df.sort_values('time', inplace=True)
    df.reset_index(inplace=True)
    data = [Energy(time=t, energy=e) for t, e in zip(df['time'], df['energy'])]
    return data

scheduler.add_job(scheduled_db_update, 'cron', day='*', hour='9')
scheduler.start()

class Energy(db.Model):
    __tablename__ = 'energy'
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime, nullable=False)
    energy = db.Column(db.Float, nullable=False)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/historicaldata', methods=['GET', 'POST'])
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

def create_historical_plot(start_date, end_date, frequency):

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
        filter(Energy.time >= start_date).filter(Energy.time <= end_date).all()
    
    dates = []
    energy_values = []
    for d in data_query:
        dates.append(d[0])
        energy_values.append(d[1])

    df = pd.DataFrame(index=dates, columns=['energy'], data=energy_values)
    df_resampled = df.resample(frequency).sum()

    return df_resampled

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)

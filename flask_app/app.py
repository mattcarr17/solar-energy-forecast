import os
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, timedelta
import plotly
import plotly.graph_objects as go
import json
import pandas as pd

app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('config.py')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

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
        yaxis_title="Energy Production",
        height=900,
        width=1300
    )

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON

def create_historical_df(start_date, end_date, frequency):
    data_query = Energy.query.with_entities(Energy.time, Energy.meter).\
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
    app.run(debug=True)

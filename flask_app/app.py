import os
from flask import Flask, render_template
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
    meter = db.Column(db.Float, nullable=False)
    inverter = db.Column(db.Float, nullable=False)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/hisoricaldata')
def show_plot():
    plot = create_recent_data_plot()
    return render_template('data-plot.html', plot=plot)


def create_recent_data_plot():
    today = datetime.today()
    yesterday = today - timedelta(days=1)
    first_index = pd.Timestamp(yesterday.year, yesterday.month, yesterday.day, 0, 0, 0)
    second_index = pd.Timestamp(today.year, today.month, today.day, 0, 0, 0)

    data_query = Energy.query.with_entities(Energy.time, Energy.inverter).\
        filter(Energy.time >= first_index).filter(Energy.time < second_index).all()
    
    dates = []
    energy_values = []
    for d in data_query:
        dates.append(d[0])
        energy_values.append(d[1])

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=energy_values
        )
    )

    fig.update_layout(
        title="Yesterday's Energy Production",
        xaxis_title="Time",
        yaxis_title="Energy Production",
        height=1000,
        width=1250
    )

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON


if __name__ == '__main__':
    app.run(debug=True)

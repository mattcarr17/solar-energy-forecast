from apscheduler.schedulers.background import BackgroundScheduler
import json
from datetime import timedelta
import pandas as pd
import requests
from app import app, db
from .models import Energy

API_KEY = app.config['API_KEY']

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
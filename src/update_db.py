import psycopg2
import pandas as pd
from datetime import timedelta
import requests 
import json

api_key = ''
url = 'http://api.eia.gov/series/?api_key={}&series_id=EBA.MISO-ALL.NG.SUN.H&num=24'.format(api_key)

resp = requests.get(url)

assert resp.status_code == 200

data = resp.json()

df = pd.DataFrame(columns=['time', 'energy'], data=data['series'][0]['data'])
df['time'] = pd.to_datetime(df['time'], utc=True).dt.tz_localize(None)

time_converter = lambda t: t - timedelta(hours=6)

df['time'] = df['time'].apply(time_converter)

df.sort_values('time', inplace=True)
df.reset_index(inplace=True)

conn = psycopg2.connect('dbname=energyapp user=postgres')

cur = conn.cursor()

for i in range(df.shape[0]):
    row = df.iloc[i]
    time = row.time
    energy = float(row.energy)
    cur.execute('''
        INSERT INTO energy (time, energy) VALUES (%s, %s);
        ''', (time, energy))

conn.commit()

cur.close()
conn.close()
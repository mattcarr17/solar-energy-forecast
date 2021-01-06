import os
import pandas as pd
import psycopg2

files = os.listdir('../data')
fl = ['../data/' + str(f) for f in files]
dfs = [pd.read_csv(f) for f in fl]
df = pd.concat(dfs)

df.columns = ['time', 'meter', 'inverter']
df.drop([0, 1], axis=0, inplace=True)
df['time'] = pd.to_datetime(df['time'])
df = df.sort_values('time')
df.set_index('time', inplace=True)
df = df.astype(float)

hourly = df.resample('H').sum()
hourly['timestamp'] = hourly.index

conn = psycopg2.connect('dbname=energyapp user=postgres password=Live.absolutely1')
cur = conn.cursor()

for i in range(hourly.shape[0]):
    row = hourly.iloc[i]
    time = pd.Timestamp(row['timestamp'])
    meter = float(row['meter'])
    inverter = float(row['inverter'])
    cur.execute("""
        INSERT INTO energy (time, meter, inverter) VALUES (%s, %s, %s);""", (time, meter, inverter)
    )

conn.commit()

cur.close()
conn.close()
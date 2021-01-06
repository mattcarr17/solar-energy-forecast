import os
import web_scraper as ws
from datetime import datetime
import pandas as pd
import psycopg2
import time

directory = '/Users/mattcarr/Desktop/work/projects/solar-energy-forecast/data'

# instantiate scraper object
scraper = ws.EnergyScraper(directory=directory)

# Download files from today and yesterday into data/
time.sleep(8)
scraper.download()
scraper.next_page()
time.sleep(5)
scraper.download()
time.sleep(3)

# Close scraper
scraper.close_driver()

# Store files in pandas dataframe
files = os.listdir('../data')
fl = ['../data/' + str(f) for f in files]
dfs = [pd.read_csv(f) for f in fl]
df = pd.concat(dfs)

# Change column names and drop first two rows (no data)
df.columns = ['time', 'meter', 'inverter']
df.drop([0, 1], axis=0, inplace=True)

# Convert time column to datetime type and sort dataframe chronologically
df['time'] = pd.to_datetime(df['time'])
df = df.sort_values('time')

# Set time as index and convert meter and inverter to float types
df.set_index('time', inplace=True)
df = df.astype(float)

# Resample dataframe to hourly time index
hourly = df.resample('H').sum()

# Create timestamp column
hourly['timestamp'] = hourly.index

# Connect to local postgres database
conn = psycopg2.connect('dbname=energyapp user=postgres password=Live.absolutely1')
cur = conn.cursor()

today = datetime.today()
current_time = pd.Timestamp(today.year, today.month, today.day, today.hour, 0, 0)

# Query last entry in database
cur.execute("""
    SELECT time FROM energy WHERE id=(SELECT max(id) FROM energy);
""")
last_entry_time = pd.Timestamp(cur.fetchone()[0])

# Filter dataframe to include records after last entry in database
# and before current time
update_data = hourly[(hourly['timestamp'] > last_entry_time) & (hourly['timestamp'] < current_time)]

# Input data to postgres database
for i in range(update_data.shape[0]):
    row = update_data.iloc[i]
    time = pd.Timestamp(row['timestamp'])
    meter = float(row['meter'])
    inverter = float(row['inverter'])
    cur.execute("""
        INSERT INTO energy (time, meter, inverter) VALUES (%s, %s, %s);""", (time, meter, inverter)
    )

# Commit changes to database
conn.commit()

# Close connection
cur.close()
conn.close()

# Delete files from data/
for f in fl:
    os.remove(f)
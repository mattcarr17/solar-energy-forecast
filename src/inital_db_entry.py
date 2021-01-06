import os
import pandas as pd
import psycopg2

# Store all files in pandas dataframe
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

# Input data to postgres database
for i in range(hourly.shape[0]):
    row = hourly.iloc[i]
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
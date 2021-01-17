from fbprophet import Prophet
import pandas as pd


def predict(data):
    model = Prophet(weekly_seasonality=False, daily_seasonality=15, yearly_seasonality=False, changepoint_prior_scale=.5)
    model.fit(data)
    future = model.make_future_dataframe(periods=24, freq='H')
    forecast = model.predict(future)
    f = forecast.iloc[-24:]
    results = f[['ds', 'yhat']]
    return results
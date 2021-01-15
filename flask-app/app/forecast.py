from fbprophet import Prophet
import pandas as pd

# class Model():

#     def __init__(self):
#         self.model = Prophet(interval_width=.5, weekly_seasonality=False, daily_seasonality=15, yearly_seasonality=False, changepoint_prior_scale=.5)
#         self.results = []

#     def train(self, data):
#         self.model.fit(data)

#     def predict(self):
#         future = self.model.make_future_dataframe(periods=24, freq='H')
#         forecast = self.model.predict(future)
#         self.results = forecast[-24:][['ds', 'yhat']]

#     def results(self):
#         plot = model.plot(self.results)
#         return (plot, self.results)

def forecast(data):
    model = Prophet(weekly_seasonality=False, daily_seasonality=15, yearly_seasonality=False, changepoint_prior_scale=.5)
    model.fit(data)
    future = model.make_future_dataframe(periods=24, freq='H')
    forecast = model.predict(future)
    f = forecast.iloc[-24:]
    results = f[['ds', 'yhat']]
    return results
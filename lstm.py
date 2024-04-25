import os
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime

url = "https://raw.githubusercontent.com/danywayGit/DownloadBinanceHistorycalData/main/GetBinanceHistoricalData.py"
filename = url.split("/")[-1]

try:
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"HTTP request returned status code {response.status_code}")
    open(filename, 'wb').write(response.content)
    print(f"File {filename} downloaded successfully")
except Exception as e:
    print("Something went wrong:", e)

from GetBinanceHistoricalData import get_binance_historical_data

# ====================== Loading Data from Binance ==================================

# ATOMUSDT cryptocurrency on 15 minutes time frame market prices
symbol    = 'ATOMUSDT'
timeframe = '15m'

# Save data to this file
file_to_save = f"{symbol}-{timeframe}.csv"

# If you haven't already saved data,
# Go ahead and grab the data from the binance API
# And store: Open time, open, high, low, close, volume values to a Pandas DataFrame
if not os.path.exists(f"{symbol}/{file_to_save}"):
    get_binance_historical_data(contract_type='spot',
                                     bulk_size='monthly',
                                     symbol=symbol, 
                                     time_frame=timeframe,
                                     start_date=datetime(2017, 1, 1),
                                     end_date=datetime.now()
        )

# If the data is already there, just load it from the CSV
else:
    print(f"File {file_to_save} already exists. Loading data from CSV")
    df = pd.read_csv(f"{symbol}/{file_to_save}")
    # usecols=['Open time', 'open', 'high', 'low', 'close', 'volume']
    
# remove the clomuns that we don't need
df = df.drop('Ignore', axis=1)    
    
# Convert the date unix to the datetime human readable format
df['Open time'] = pd.to_datetime(df['Open time'], unit='ms')
df['Close time'] = pd.to_datetime(df['Close time'], unit='ms')
    
# Sort DataFrame by date
df = df.sort_values('Open time')

# First calculate the mid prices from the highest and lowest
# The as_matrix() method was deprecated in version 0.23.0 of pandas and removed in version 1.0.0.
# to_numpy() method is use instead.
high_prices = df.loc[:,'High'].to_numpy()
low_prices = df.loc[:,'Low'].to_numpy()
mid_prices = (high_prices+low_prices)/2.0

# How many data points we have
num_rows = len(df)
print(f"Number of data points: {num_rows}")

mid_nb_rows = int(num_rows / 2)
print(f"Half of data points number: {mid_nb_rows}")

third_nb_rows = int(num_rows / 3)
print(f"Third of data points number: {third_nb_rows}")


# Split the data into training/testing sets
train_data = mid_prices[:mid_nb_rows]
test_data = mid_prices[mid_nb_rows:]

# Scale the data to be between 0 and 1
# When scaling remember! You normalize both test and train data with respect to training data
# Because you are not supposed to have access to test data
#  MinMaxScaler is a function from the scikit-learn library.
#  The code then reshapes the training and test data to be a single column using the reshape() function with the argument -1, which means that the number of rows is inferred from the length of the array and the number of columns is set to 1.
# This is necessary because the MinMaxScaler function expects a 2D array as input.
scaler = MinMaxScaler()
train_data = train_data.reshape(-1,1)
test_data = test_data.reshape(-1,1)

print(train_data)
print(test_data)

input("Press Enter to continue...")


# Double check the result
print(df.head())

# data visualization
plt.figure(figsize = (18,9))
plt.plot(range(df.shape[0]),(df['Low']+df['High'])/2.0)
plt.xticks(range(0,df.shape[0],2500),df['Open time'].loc[::2500],rotation=60)
plt.xlabel('Open time',fontsize=18)
plt.ylabel('Mid Price',fontsize=18)
plt.show()
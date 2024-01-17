import scipy.special as sp
import pandas as pd
import numpy as np

data_file = 'data/solar_historical_data.csv'

def read_data(data_file):
    #Clean data from irradiation ready to process
    with open(data_file, newline='') as weather_data:
        irradiance = pd.read_csv(weather_data, skiprows=42, delimiter=';')
        irradiance.rename(columns={irradiance.columns[0]: irradiance.columns[0].lstrip('# ')}, inplace=True)
        irradiance['index_date'] = irradiance['Observation period'].apply(lambda x: x.split('/')[0])
        irradiance['index_date'] = pd.to_datetime(irradiance['index_date'])
        irradiance.set_index(irradiance['index_date'], inplace=True)
        irradiance = irradiance[['DHI', 'GHI']]
    return irradiance 

def data_normalization(irradiance_data):
    # Normalize the data from PD
    data_min = irradiance_data['GHI'].min()
    data_max = irradiance_data['GHI'].max()
    normalized_data = (irradiance_data - data_min) / (data_max - data_min)
    return normalized_data

def beta_alpha_stimation(data_mean, data_std):
    for i, _ in enumerate(data_mean):
        if data_std.iloc[i] > 0:
            beta_values['b'].iloc[i] = (1 - data_mean.iloc[i]) * ((data_mean.iloc[i] * (1 + data_mean.iloc[i])) / (data_std.iloc[i]**2) - 1)
            beta_values['a'].iloc[i] = (data_mean.iloc[i] * beta_values['b'].iloc[i]) / (1 - data_mean.iloc[i])
        else:
            beta_values['b'].iloc[i] = 0
            beta_values['a'].iloc[i] = 0
    return beta_values

def beta_PDF_function(beta_values, day, time):
    position = ((day - 1) * 24) + time
    s = np.random.rand()
    value = (sp.gamma(beta_values['a'].iloc[position] + beta_values['b'].iloc[position]) / (sp.gamma(beta_values['a'].iloc[position]) * sp.gamma(beta_values['b'].iloc[position])) ) * s * (1-s)**(beta_values['b'].iloc[position] - 1)
    return value

# Read data and clean data
historical_irradiance = read_data(data_file)
beta_values = pd.DataFrame(np.nan, index=range(len(historical_irradiance)),columns=['a','b'])

# Normalize data
normalized_irradiance = data_normalization(historical_irradiance)

# Estimate parameters for beta distribution
data_mean = normalized_irradiance['GHI'].groupby(normalized_irradiance.index.strftime('%m-%d %H')).mean()
data_std = normalized_irradiance['GHI'].groupby(normalized_irradiance.index.strftime('%m-%d %H')).std()

beta_values = beta_alpha_stimation(data_mean, data_std)
beta_values.to_csv('data/beta_values.csv')

# Beta PDF equation calculation
day = 15
time = 10 # in 24 hours format
irradiance_prediction = beta_PDF_function(beta_values, day, time)
print(irradiance_prediction)


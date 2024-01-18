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
    normalized_data = ((irradiance_data - data_min) / (data_max - data_min))/1000
    return normalized_data

def beta_alpha_stimation(data_mean, data_std):
    beta_values = pd.DataFrame(index=data_mean.index, columns=['a','b'])
    valid_mask = data_std > 0
    beta_values.loc[valid_mask, 'b'] = (1 - data_mean[valid_mask]) * (((data_mean[valid_mask] * (1 + data_mean[valid_mask])) / (data_std[valid_mask]**2)) - 1)
    beta_values.loc[valid_mask, 'a'] = (data_mean[valid_mask] * beta_values['b'][valid_mask]) / (1 - data_mean[valid_mask])
    beta_values.loc[~valid_mask, ['a', 'b']] = 0
    return beta_values

def beta_PDF_function(beta_values, day, time):
    position = ((day - 1) * 24) + time
    s = 0.2
    alpha = beta_values['a'].iloc[position]
    beta = beta_values['b'].iloc[position]
    beta_function_value = sp.beta(alpha, beta)
    pdf_value = (s ** (alpha - 1)) * ((1-s) ** (beta - 1)) / beta_function_value
    return pdf_value

# Read data and clean data
historical_irradiance = read_data(data_file)

# Normalize data
normalized_irradiance = data_normalization(historical_irradiance)

# Estimate parameters for beta distribution
data_mean = normalized_irradiance['GHI'].groupby(normalized_irradiance.index.strftime('%m-%d %H')).mean()
data_std = normalized_irradiance['GHI'].groupby(normalized_irradiance.index.strftime('%m-%d %H')).std()

beta_values = beta_alpha_stimation(data_mean, data_std)
beta_values.to_csv('data/beta_values.csv')

# Beta PDF equation calculation
irradiance_prediction = beta_PDF_function(beta_values, day=15, time=12)
print(irradiance_prediction)


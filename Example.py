import pandas as pd
import time
import numpy as np
import matplotlib.pyplot as plt
import requests
from Bill_Calc import bill_calculator as calc
import plotly as py
import plotly.graph_objs as go

# Creating sample load
t0 = time.time()
TestData = pd.read_csv('D:/Dropbox/Database/Load/SGSC/ProcessedData/General_filtered.csv')
print(time.time() - t0)  # takes 59 s to load

NumNan = TestData.isna().sum() / TestData.shape[0] * 100
NumNan2 = NumNan[NumNan < 1].copy()
NumNan2.index[1:101]

SampleData = TestData[TestData.columns.intersection(NumNan2.index[0:101])].copy()
SampleData = SampleData[SampleData['READING_DATETIME'] < '2013-07-01 00:30:00'].copy()
SampleData.to_csv('SampleLoadProfile.csv')

NetworkLoad = pd.DataFrame({'Datetime': TestData['READING_DATETIME']})
NetworkLoad['kWh'] = np.nansum(TestData.iloc[:, 1:].values, axis=1)
NetworkLoad = NetworkLoad[NetworkLoad['Datetime'] < '2013-07-01 00:30:00'].copy()
NetworkLoad.to_csv('NetworkLoad.csv')

# Reading data (start here)
LoadProfiles = pd.read_csv('SampleLoadProfile.csv')
LoadProfiles['Datetime'] = pd.to_datetime(LoadProfiles['Datetime'], format='%d/%m/%Y %H:%M')

NetworkLoad = pd.read_csv('NetworkLoad.csv')
NetworkLoad['Datetime'] = pd.to_datetime(NetworkLoad['Datetime'], format='%d/%m/%Y %H:%M')
NetworkLoad.set_index('Datetime', inplace=True)
NetworkLoad.columns = ['NetworkLoad']

SolarProf = pd.read_csv('100SolarProf.csv')
SolarProf['Datetime'] = pd.to_datetime(SolarProf['Datetime'], format='%d/%m/%Y %H:%M')

CombinedLoad = LoadProfiles.merge(SolarProf, on='Datetime')

NetLoad = pd.concat([CombinedLoad['Datetime'], pd.DataFrame(
    data=CombinedLoad[CombinedLoad.columns[1:101]].values - CombinedLoad[CombinedLoad.columns[101:]].values)], axis=1)

# CoincidentPeak_ind = NetworkLoad[].idxmax()

# Take a look at the load:
data = [{"x": LoadProfiles['Datetime'], "y": LoadProfiles[col]} for col in LoadProfiles.columns[1:10]]
layout = go.Layout(showlegend=True, title='First 10 homes')
py.offline.plot({"data": data, "layout": layout})

Allsum = LoadProfiles.sum()

data = [go.Histogram(x=Allsum / 365)]
py.offline.plot({"data": data, "layout": layout})

# testing a tariff

# Tariff - this will be selected by used from a list of tariffs in the dropdown list here we use a sample for testing

all_tariffs = requests.get('http://api.ceem.org.au/elec-tariffs/retail')

all_tariffs_list = all_tariffs.json()

# sample flat rate tariff
Tariff_name_R_FR = "Origin Flat Rate NSW (Endeavour area)"
# sample tou tariff
Tariff_name_R_TOU = "Energy Locals TOU ACT"

for i in range(len(all_tariffs_list)):
    if all_tariffs_list[i]['Name'] == Tariff_name_R_TOU:
        selected_tariff = all_tariffs_list[i]

tariff = selected_tariff
load_profile = LoadProfiles.copy().set_index('Datetime')

Results = calc(load_profile, tariff)

SGSC_kWh = pd.concat([pd.to_datetime(TestData['READING_DATETIME']), TestData.iloc[:, 1:].astype('float32')],
                     axis=1).reset_index(drop=True)
SGSC_kWh_sum = pd.concat([SGSC_kWh['READING_DATETIME'], pd.DataFrame(np.nansum(SGSC_kWh.iloc[:, 1:].values, axis=1),
                                                                     columns=['Sum'])], axis=1).reset_index(drop=True)

# plt.figure()
# plt.plot(SGSC_kWh['READING_DATETIME'], SGSC_kWh_sum['Sum'])


SGSC_kWh_Daily = np.nansum(SGSC_kWh.iloc[:, 1:].values, axis=0)

# plt.figure()
# plt.hist(SGSC_kWh_Daily, 100)

# filter to only 2013
SGSC_kWh_2013 = SGSC_kWh[SGSC_kWh['READING_DATETIME'] > '2013-01-01 00:00:00'].copy().set_index('READING_DATETIME')
# finding the missing values
NumNonNan = (len(SGSC_kWh_2013) - SGSC_kWh_2013.count()) / len(SGSC_kWh_2013.iloc[:, 1:])
# filtering those which have more than 5% missing value
GoodHomes = NumNonNan.index[NumNonNan < 0.05].tolist()

# sample
# plt.figure()
# plt.plot(SGSC_kWh_2013.index, SGSC_kWh_2013['8144683'])

# filter to good homes
SGSC_kWh_2013 = SGSC_kWh_2013.iloc[:, SGSC_kWh_2013.columns.isin(GoodHomes)]

Tariff_name_N_FR = "Essential Energy Flat Rate NSW 2017/18"
Tariff_name_N_TOU = "Ausgrid TOU NSW 2017/18"
Tariff_name_N_Dem = "CitiPower Demand Charge VIC 2017/18"
Tariff_name_N_Block = "Ergon Block (West) QLD 2017/18"
Tariff_name_N_Block_Q = "AusNet Block_Quarterly VIC 2017/18"
Tariff_name_N_Demand = "Powercor Demand Charge VIC 2019 (Residential)"

all_tariffs_Network = requests.get('http://api.ceem.org.au/elec-tariffs/network')

all_tariffs_list = all_tariffs_Network.json()
all_tariffs_list = all_tariffs_list[0]['Tariffs']
for i in range(len(all_tariffs_list)):
    if all_tariffs_list[i]['Name'] == Tariff_name_N_Demand:
        selected_tariff = all_tariffs_list[i]

tariff = selected_tariff




load_profile = SGSC_kWh_2013.copy()
load_profile.info()

Results = calc(load_profile, tariff)


# Using full sgsc homes

t0=time.time()
LoadkWh = pd.read_csv('D:/Dropbox/Database/Load/SGSC/ProcessedData/General_filtered.csv')
print(time.time()-t0)

LoadkWh['READING_DATETIME'] = pd.to_datetime(LoadkWh['READING_DATETIME'], format='%Y-%m-%d %H:%M:%S')
LoadkWh = LoadkWh[LoadkWh['READING_DATETIME'] <= '2013-07-01 00:00:00'].copy()

# Missing data check (removing any home with more than 5% missing data)
LoadkWh = LoadkWh.loc[:, LoadkWh.isnull().sum() / LoadkWh.shape[0] < 0.05].copy()
LoadkWh = LoadkWh.fillna(0)  # Filling the missing values with zero (filling with other methods is dangerous for tariff analysis..)
load_profile_b = LoadkWh.copy().set_index('READING_DATETIME')

#

# testing
load_profile = LoadProfiles.copy().set_index('Datetime')  # small load
load_profile = load_profile_b.copy()  # big load
load_profile.reset_index(inplace=True)
load_profile.rename(columns={'READING_DATETIME': 'Datetime'},inplace=True)
load_profile = load_profile.set_index('Datetime')

# changing the energy to FlatRate
for k, v in tariff['Parameters'].items():
    v['FlatRate'] = v['Energy']
    del (v['Energy'])

for k, v in tariff['Parameters'].items():
    for k2, v2 in v['Demand'].items():
        v2['Weekday'] = v2['Workday']
        v2['Weekend'] = v2['Weekend and Public Holidays']
for k, v in tariff['Parameters'].items():
    v['Daily'] = v['Yearly'].copy()
    v['Daily']['Value'] = v['Yearly']['Value']/365


# changing the energy to Blockannual
for k, v in tariff['Parameters'].items():
    v['BlockAnnual'] = v['Energy']
    del (v['Energy'])

#  to quarterly
for k, v in tariff['Parameters'].items():
    v['BlockQuarterly'] = v['Energy']
    del (v['Energy'])

#  to monthly

for k, v in tariff['Parameters'].items():
    v['BlockMonthly'] = v['Energy']
    del (v['Energy'])

#  to TOU
for k, v in tariff['Parameters'].items():
    v['TOU'] = v['Energy']
    del (v['Energy'])


# Changes:
# Energy to FlatRate or BlockAnnual or BlockQuarterly or BlockMonthly or TOU
# working holiday etc to weekday weekend
# network load columns should be called 'Datetime', 'NetworkLoad'
# network_load.columns = ['Datetime', 'NetworkLoad'] and should match the dates


results2= bill_calculator(load_profile, tariff, network_load=None, fit=True)
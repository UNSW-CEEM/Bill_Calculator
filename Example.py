
import pandas as pd
import time
import numpy as np
import matplotlib.pyplot as plt
import requests
from Bill_Calc import bill_calculator as calc


t0 = time.time()
TestData = pd.read_csv('D:/Dropbox/Database/Load/SGSC/ProcessedData/General_filtered.csv')
print(time.time()-t0) # takes 59 s to load


SGSC_kWh = pd.concat([pd.to_datetime(TestData['READING_DATETIME']), TestData.iloc[:, 1:].astype('float32')],
                     axis=1).reset_index(drop=True)
SGSC_kWh_sum = pd.concat([SGSC_kWh['READING_DATETIME'], pd.DataFrame(np.nansum(SGSC_kWh.iloc[:, 1:].values, axis=1),
                                                                     columns=['Sum'])], axis=1).reset_index(drop=True)

#plt.figure()
#plt.plot(SGSC_kWh['READING_DATETIME'], SGSC_kWh_sum['Sum'])


SGSC_kWh_Daily = np.nansum(SGSC_kWh.iloc[:, 1:].values, axis=0)

#plt.figure()
#plt.hist(SGSC_kWh_Daily, 100)

# filter to only 2013
SGSC_kWh_2013 = SGSC_kWh[SGSC_kWh['READING_DATETIME'] > '2013-01-01 00:00:00'].copy().set_index('READING_DATETIME')
# finding the missing values
NumNonNan = (len(SGSC_kWh_2013) - SGSC_kWh_2013.count())/len(SGSC_kWh_2013.iloc[:, 1:])
# filtering those which have more than 5% missing value
GoodHomes = NumNonNan.index[NumNonNan < 0.05].tolist()

# sample
#plt.figure()
#plt.plot(SGSC_kWh_2013.index, SGSC_kWh_2013['8144683'])

# filter to good homes
SGSC_kWh_2013 = SGSC_kWh_2013.iloc[:, SGSC_kWh_2013.columns.isin(GoodHomes)]

# testing a tariff

# Tariff - this will be selected by used from a list of tariffs in the dropdown list here we use a sample for testing

all_tariffs = requests.get('http://api.ceem.org.au/elec-tariffs/retail')

# sample flat rate tariff
Tariff_name_R_FR = "Origin Flat Rate NSW (Endeavour area)"
# sample tou tariff
Tariff_name_R_TOU = "Energy Locals TOU ACT"

all_tariffs_Network = requests.get('http://api.ceem.org.au/elec-tariffs/network')

Tariff_name_N_FR = "Essential Energy Flat Rate NSW 2017/18"
Tariff_name_N_TOU = "Ausgrid TOU NSW 2017/18"


all_tariffs_list = all_tariffs_Network.json()
for i in range(len(all_tariffs_list)):
    if all_tariffs_list[i]['Name'] == Tariff_name_N_TOU:
        selected_tariff = all_tariffs_list[i]


tariff = selected_tariff
load_profile = SGSC_kWh_2013.copy()
load_profile.info()

Results = calc(load_profile, tariff)
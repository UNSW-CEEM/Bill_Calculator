import pandas as pd
import time
from Bill_Calc import bill_calculator as calc
import json

# load load data
LoadProfiles = pd.read_csv('SampleLoadProfile.csv')
LoadProfiles['Datetime'] = pd.to_datetime(LoadProfiles['Datetime'], format='%d/%m/%Y %H:%M')

NetworkLoad = pd.read_csv('NetworkLoad.csv')
NetworkLoad['Datetime'] = pd.to_datetime(NetworkLoad['Datetime'], format='%d/%m/%Y %H:%M')
NetworkLoad.set_index('Datetime', inplace=True)
NetworkLoad.columns = ['NetworkLoad']


# Load tariff
with open('AllTariffs_Network.json') as f:
    all_tariffs_list = json.load(f)
all_tariffs_list = all_tariffs_list[0]['Tariffs']

AllRes = {}
k = 1

for tariff in all_tariffs_list:
    print(tariff)
    k = k + 1
    AllRes[tariff['Tariff ID']] = calc(LoadProfiles.set_index('Datetime'), tariff)


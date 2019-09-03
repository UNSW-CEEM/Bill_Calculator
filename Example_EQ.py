import pandas as pd
import json
from Bill_Calc import bill_calculator as calc
import copy

import warnings
warnings.filterwarnings("ignore")


# Load profile
LoadProfiles = pd.read_csv('SampleLoadProfile.csv')
LoadProfiles['Datetime'] = pd.to_datetime(LoadProfiles['Datetime'],format='%d/%m/%Y %H:%M')
load_profile = LoadProfiles.copy().set_index('Datetime')

# Load tariff
with open('EQTariffTemplates.json') as f:
    all_tariffs_list2 = json.load(f)


## Example of Inclining Block Tariff
Tariff_name = "Inclining Block Tariff"
for i in range(len(all_tariffs_list2)):
    if all_tariffs_list2[i]['Name'] == Tariff_name:
        tariff = all_tariffs_list2[i]

# Check the tariff:
print(tariff)

# changing the parameters as required:
tariff['Parameters']['NUOS']['Energy']['Block1']['Value'] = 1.5
tariff['Parameters']['NUOS']['Energy']['Block2']['Value'] = 2.5
tariff['Parameters']['NUOS']['Energy']['Block3']['Value'] = 3.5

Results_old = bill_calculator(load_profile, tariff)

tariff['Parameters']['NUOS']['BlockAnnual'] = tariff['Parameters']['NUOS']['Energy']
Results_new = bill_calculator_new(load_profile, tariff)


## Example of Residential Flat
Tariff_name = "Residential Flat"
for i in range(len(all_tariffs_list2)):
    if all_tariffs_list2[i]['Name'] == Tariff_name:
        tariff = all_tariffs_list2[i]

# Check the tariff:
print(tariff)

# changing the parameters as required:
tariff['Parameters']['NUOS']['Energy']['Value'] = 1.5
tariff['Parameters']['NUOS']['Daily']['Value'] = 1

Results_old = bill_calculator(load_profile, tariff)
tariff['Parameters']['NUOS']['FlatRate'] = tariff['Parameters']['NUOS']['Energy']
Results_new = bill_calculator_new(load_profile, tariff)

# Example Residential Basic
Tariff_name = "Residential Basic"
for i in range(len(all_tariffs_list2)):
    if all_tariffs_list2[i]['Name'] == Tariff_name:
        tariff = all_tariffs_list2[i]

# Check the tariff:
print(tariff)

# changing the parameters as required:
tariff['Parameters']['NUOS']['Energy']['Block1']['Value'] = 1.5
tariff['Parameters']['NUOS']['Energy']['Block2']['Value'] = 1

Results_old = bill_calculator(load_profile, tariff)
tariff['Parameters']['NUOS']['BlockAnnual'] = tariff['Parameters']['NUOS']['Energy']
Results_new = bill_calculator_new(load_profile, tariff)

# Example Residential Demand
Tariff_name = "Residential Demand"
for i in range(len(all_tariffs_list2)):
    if all_tariffs_list2[i]['Name'] == Tariff_name:
        tariff = all_tariffs_list2[i]

# Check the tariff:
print(tariff)

# changing the parameters as required:
tariff['Parameters']['NUOS']['Demand']['Day']['Value'] = 5
tariff['Parameters']['NUOS']['Demand']['Evening']['Value'] = 10
tariff['Parameters']['NUOS']['Energy']['Value'] = 2
tariff['Parameters']['NUOS']['Daily']['Value'] = 1

Results_old = bill_calculator(load_profile, tariff)
tariff['Parameters']['NUOS']['FlatRate'] = tariff['Parameters']['NUOS']['Energy']
Results_new = bill_calculator_new(load_profile, tariff)

with open('EQTariffTemplates.json') as f:
    all_tariffs_list2 = json.load(f)

# Example Residential Capacity
Tariff_name = "Residential Capacity"
for i in range(len(all_tariffs_list2)):
    if all_tariffs_list2[i]['Name'] == Tariff_name:
        tariff = all_tariffs_list2[i]

# Check the tariff:
print(tariff)

# changing the parameters as required:
tariff['Parameters']['NUOS']['Demand']['Day']['Value'] = 5
tariff['Parameters']['NUOS']['Demand']['Day']['Capacity']['Value'] = 3
tariff['Parameters']['NUOS']['Demand']['Day']['Capacity Exceeded No'] = 1

tariff['Parameters']['NUOS']['Demand']['Evening']['Value'] = 10
tariff['Parameters']['NUOS']['Demand']['Evening']['Capacity']['Value'] = 3
tariff['Parameters']['NUOS']['Demand']['Evening']['Capacity Exceeded No'] = 1

tariff['Parameters']['NUOS']['Energy']['Value'] = 2
tariff['Parameters']['NUOS']['Daily']['Value'] = 1


Results_old = bill_calculator(load_profile, tariff)
tariff['Parameters']['NUOS']['FlatRate'] = tariff['Parameters']['NUOS']['Energy']
Results_new = bill_calculator_new(load_profile, tariff)

#  Testing annual and block
LoadProfiles = pd.read_csv('SampleLoadProfile.csv')
LoadProfiles['Datetime']=pd.to_datetime(LoadProfiles['Datetime'],format='%d/%m/%Y %H:%M')
load_profile = LoadProfiles.copy().set_index('Datetime')


# Load tariff
with open('EQTariffTemplates.json') as f:
    all_tariffs_list2 = json.load(f)

## Quarterly Block Tariff
Tariff_name = "Inclining Block Tariff"
for i in range(len(all_tariffs_list2)):
    if all_tariffs_list2[i]['Name'] == Tariff_name:
        tariff = all_tariffs_list2[i]

# Check the tariff:
print(tariff)

# changing the parameters as required:
tariff['Parameters']['NUOS']['Energy']['Block1']['Value'] = 1.5
tariff['Parameters']['NUOS']['Energy']['Block2']['Value'] = 2.5
tariff['Parameters']['NUOS']['Energy']['Block3']['Value'] = 3.5

tariff['Parameters']['NUOS']['Daily']['Value'] = 3
tariff['Type']='Block_Quarterly'
Results = calc(load_profile, tariff)

## Annual Block Tariff
Tariff_name = "Inclining Block Tariff"
for i in range(len(all_tariffs_list2)):
    if all_tariffs_list2[i]['Name'] == Tariff_name:
        tariff = all_tariffs_list2[i]

# Check the tariff:
print(tariff)

# changing the parameters as required:
tariff['Parameters']['NUOS']['Energy']['Block1']['Value'] = 1.5
tariff['Parameters']['NUOS']['Energy']['Block2']['Value'] = 2.5
tariff['Parameters']['NUOS']['Energy']['Block3']['Value'] = 3.5

tariff['Parameters']['NUOS']['Daily']['Value'] = 3
tariff['Type']='Block_Annual'
Results = calc(load_profile, tariff)

with open('EQTariffTemplates.json') as f:
    all_tariffs_list2 = json.load(f)

## Monthly Block Tariff
Tariff_name = "Inclining Block Tariff"
for i in range(len(all_tariffs_list2)):
    if all_tariffs_list2[i]['Name'] == Tariff_name:
        tariff = all_tariffs_list2[i]

# Check the tariff:
print(tariff)

# changing the parameters as required:
tariff['Parameters']['NUOS']['Energy']['Block1']['Value'] = 1.5
tariff['Parameters']['NUOS']['Energy']['Block2']['Value'] = 2.5
tariff['Parameters']['NUOS']['Energy']['Block3']['Value'] = 3.5

tariff['Parameters']['NUOS']['Daily']['Value'] = 3
tariff['Type'] = 'Block_Monthly'
Results_old = bill_calculator(load_profile, tariff)
tariff['Parameters']['NUOS']['BlockMonthly'] = tariff['Parameters']['NUOS']['Energy']
Results_new = bill_calculator_new(load_profile, tariff)
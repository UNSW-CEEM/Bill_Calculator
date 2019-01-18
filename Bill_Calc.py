import numpy as np
import pandas as pd
import time
import sys

def bill_calculator(load_profile, tariff):

    def pre_processing_load(load_profile):

        # placeholder for a quick quality check function for load profile
        # make sure it is kwh
        # make sure it is one year
        # make sure it doesn't have missing value or changing the missing values to zero or to average
        # make sure the name is Load
        # time interval is half hour
        return load_profile

    def fr_calc(load_profile, tariff):

        f_load_profile = load_profile
        imports = [np.nansum(f_load_profile[col].values[f_load_profile[col].values > 0])
                   for col in f_load_profile.columns if col != 'READING_DATETIME']
        Results = pd.DataFrame(index=[col for col in f_load_profile.columns if col != 'READING_DATETIME'],
                               data=imports, columns=['Annual_kWh'])
        Results['Annual_kWh_exp'] = [-1 * np.nansum(f_load_profile[col].values[f_load_profile[col].values < 0])
                                     for col in f_load_profile.columns if col != 'READING_DATETIME']
        if tariff['ProviderType'] == 'Retailer':
            Results['DailyCharge'] = len(load_profile.index.normalize().unique()) * tariff['Parameters']['Daily']['Value']
            Results['EnergyCharge'] = Results['Annual_kWh'] * tariff['Parameters']['Energy']['Value']
            Results['EnergyCharge_Discounted'] = Results['EnergyCharge'] * (1 - tariff['Discount (%)'] / 100)
            Results['Fit_Rebate'] = Results['Annual_kWh_exp'] * tariff['Parameters']['FiT']['Value']
            Results['Bill'] = Results['DailyCharge'] + Results['EnergyCharge'] - Results['Fit_Rebate']
        else:
            for TarComp, TarCompVal in tariff['Parameters'].items():
                Results[TarComp, 'DailyCharge'] = len(load_profile.index.normalize().unique()) * TarCompVal['Daily']['Value']
                Results[TarComp, 'EnergyCharge'] = Results['Annual_kWh'] * TarCompVal['Energy']['Value']
            Results['Bill'] = Results['NUOS','DailyCharge'] + Results['NUOS','EnergyCharge']
        return Results

    def block_annual(load_profile, tariff):

        f_load_profile = load_profile
        imports = [np.nansum(f_load_profile[col].values[f_load_profile[col].values > 0])
                   for col in f_load_profile.columns if col != 'READING_DATETIME']
        Results = pd.DataFrame(index=[col for col in f_load_profile.columns if col != 'READING_DATETIME'],
                               data=imports, columns=['Annual_kWh'])
        Results['Annual_kWh_exp'] = [-1 * np.nansum(f_load_profile[col].values[f_load_profile[col].values < 0])
                                     for col in f_load_profile.columns if col != 'READING_DATETIME']
        if tariff['ProviderType'] == 'Retailer':
            tariff_temp = tariff.copy()
            del tariff_temp['Parameters']
            tariff_temp['Parameters'] = {'Retailer': tariff['Parameters']}
            tariff = tariff_temp.copy()


        for TarComp, TarCompVal in tariff['Parameters'].items():
            Results[TarComp, 'DailyCharge'] = len(load_profile.index.normalize().unique()) * TarCompVal['Daily'][
                'Value']
            BlockUse = Results[['Annual_kWh']].copy()
            BlockUseCharge = Results[['Annual_kWh']].copy()

            lim = 0
            for k, v in TarCompVal['Energy'].items():
                BlockUse[k] = BlockUse['Annual_kWh']
                BlockUse[k][BlockUse[k] > v['HighBound']]= v['HighBound']
                BlockUse[k] = BlockUse[k]-lim
                BlockUse[k][BlockUse[k] < 0] = 0
                lim = v['HighBound']
                BlockUseCharge[k] = BlockUse[k] * v['Value']
            del BlockUse['Annual_kWh']
            del BlockUseCharge['Annual_kWh']
            Results[TarComp, 'EnergyCharge'] = BlockUseCharge.sum(axis=1)
            if 'Discount (%)' in tariff:
                Results[TarComp, 'EnergyCharge_Discounted'] = Results[TarComp, 'EnergyCharge'] * (
                            1 - tariff['Discount (%)'] / 100)
            else:
                Results[TarComp, 'EnergyCharge_Discounted'] = Results[TarComp, 'EnergyCharge']
            if 'FiT' in TarCompVal:
                Results[TarComp, 'Fit_Rebate'] = Results['Annual_kWh_exp'] * TarCompVal['FiT']['Value']
            else:
                Results[TarComp, 'Fit_Rebate'] = 0
        if tariff['ProviderType'] == 'Retailer':
            Results['Bill'] = Results['Retailer', 'DailyCharge'] + Results['Retailer', 'EnergyCharge_Discounted'] - \
                              Results['Retailer', 'Fit_Rebate']
        else:
            Results['Bill'] = Results['NUOS', 'DailyCharge'] + Results['NUOS', 'EnergyCharge_Discounted'] - Results[
                'NUOS', 'Fit_Rebate']


        return Results

    def block_quarterly(load_profile, tariff):

        load_profile_imp=load_profile.clip_lower(0)
        load_profile_Q1 = load_profile_imp.loc[load_profile_imp.index.month.isin([1, 2, 3]), :]
        load_profile_Q2 = load_profile_imp.loc[load_profile_imp.index.month.isin([4, 5, 6]), :]
        load_profile_Q3 = load_profile_imp.loc[load_profile_imp.index.month.isin([7, 8, 9]), :]
        load_profile_Q4 = load_profile_imp.loc[load_profile_imp.index.month.isin([10, 11, 12]), :]
        f_load_profile = load_profile
        imports = [np.nansum(f_load_profile[col].values[f_load_profile[col].values > 0])
                   for col in f_load_profile.columns if col != 'READING_DATETIME']
        Results = pd.DataFrame(index=[col for col in f_load_profile.columns if col != 'READING_DATETIME'],
                               data=imports, columns=['Annual_kWh'])
        Results['Q1_kWh'] = load_profile_Q1.sum()
        Results['Q2_kWh'] = load_profile_Q2.sum()
        Results['Q3_kWh'] = load_profile_Q3.sum()
        Results['Q4_kWh'] = load_profile_Q4.sum()
        Results['Annual_kWh_exp'] = [-1 * np.nansum(f_load_profile[col].values[f_load_profile[col].values < 0])
                                     for col in f_load_profile.columns if col != 'READING_DATETIME']
        if tariff['ProviderType'] == 'Retailer':
            tariff_temp = tariff.copy()
            del tariff_temp['Parameters']
            tariff_temp['Parameters'] = {'Retailer': tariff['Parameters']}
            tariff = tariff_temp.copy()
        for TarComp, TarCompVal in tariff['Parameters'].items():
            Results[TarComp, 'DailyCharge'] = len(load_profile.index.normalize().unique()) * TarCompVal['Daily'][
                'Value']
            for i in range(1,5):
                BlockUse = Results[['Q{}_kWh'.format(i)]].copy()
                BlockUseCharge = BlockUse.copy()
                lim = 0
                for k, v in TarCompVal['Energy'].items():
                    BlockUse[k] = BlockUse['Q{}_kWh'.format(i)]
                    BlockUse[k][BlockUse[k] > v['HighBound']] = v['HighBound']
                    BlockUse[k] = BlockUse[k] - lim
                    BlockUse[k][BlockUse[k] < 0] = 0
                    lim = v['HighBound']
                    BlockUseCharge[k] = BlockUse[k] * v['Value']
                del BlockUse['Q{}_kWh'.format(i)]
                del BlockUseCharge['Q{}_kWh'.format(i)]

                Results[TarComp, 'EnergyCharge_Q{}'.format(i)] = BlockUseCharge.sum(axis=1)
            Results[TarComp, 'EnergyCharge'] = Results[TarComp, 'EnergyCharge_Q1'] +Results[TarComp, 'EnergyCharge_Q2']\
                                               +Results[TarComp, 'EnergyCharge_Q3']+Results[TarComp, 'EnergyCharge_Q4']
            if 'Discount (%)' in tariff:
                Results[TarComp, 'EnergyCharge_Discounted'] = Results[TarComp, 'EnergyCharge'] * (
                        1 - tariff['Discount (%)'] / 100)
            else:
                Results[TarComp, 'EnergyCharge_Discounted'] = Results[TarComp, 'EnergyCharge']
            if 'FiT' in TarCompVal:
                Results[TarComp, 'Fit_Rebate'] = Results['Annual_kWh_exp'] * TarCompVal['FiT']['Value']
            else:
                Results[TarComp, 'Fit_Rebate'] = 0
        if tariff['ProviderType'] == 'Retailer':
            Results['Bill'] = Results['Retailer', 'DailyCharge'] + Results['Retailer', 'EnergyCharge_Discounted'] - \
                              Results['Retailer', 'Fit_Rebate']
        else:
            Results['Bill'] = Results['NUOS', 'DailyCharge'] + Results['NUOS', 'EnergyCharge_Discounted'] - Results[
                'NUOS', 'Fit_Rebate']
        return Results
    def tou_calc(load_profile, tariff):
        t0 = time.time()
        f_load_profile = load_profile
        imports = [np.nansum(f_load_profile[col].values[f_load_profile[col].values > 0])
                   for col in f_load_profile.columns if col != 'READING_DATETIME']
        Results = pd.DataFrame(index=[col for col in f_load_profile.columns if col != 'READING_DATETIME'],
                               data=imports, columns=['Annual_kWh'])
        Results['Annual_kWh_exp'] = [-1 * np.nansum(f_load_profile[col].values[f_load_profile[col].values < 0])
                                     for col in f_load_profile.columns if col != 'READING_DATETIME']
        if tariff['ProviderType'] == 'Retailer':
            tariff_temp = tariff.copy()
            del tariff_temp['Parameters']
            tariff_temp['Parameters'] = {'Retailer': tariff['Parameters']}
            tariff = tariff_temp.copy()
        for TarComp, TarCompVal in tariff['Parameters'].items():
            Results[TarComp,'DailyCharge'] = len(load_profile.index.normalize().unique()) * TarCompVal['Daily']['Value']
            time_ind = np.zeros(load_profile.shape[0])
            load_profile_TI = pd.DataFrame()
            load_profile_TI_Charge = pd.DataFrame()
            ti = 0
            for k, v in TarCompVal['Energy'].items():
                this_part = v.copy()
                ti += 1
                for k2, v2, in this_part['TimeIntervals'].items():
                    start_hour = int(v2[0][0:2])
                    if start_hour == 24:
                        start_hour = 0
                    start_min = int(v2[0][3:5])
                    end_hour = int(v2[1][0:2])
                    if end_hour == 0:
                        end_hour = 24
                    end_min = int(v2[1][3:5])
                    if this_part['Weekday']:
                        if start_hour <= end_hour:
                            time_ind = np.where((load_profile.index.weekday < 5) &
                                                (load_profile.index.month.isin(this_part['Month'])) &
                                                (((60 * load_profile.index.hour + load_profile.index.minute)
                                                  >= (60 * start_hour + start_min)) &
                                                 ((60 * load_profile.index.hour + load_profile.index.minute)
                                                  < (60 * end_hour + end_min))), ti,
                                                time_ind)
                        else:
                            time_ind = np.where((load_profile.index.weekday < 5) &
                                                                (load_profile.index.month.isin(this_part['Month'])) &
                                                                (((60 * load_profile.index.hour + load_profile.index.minute)
                                                                  >= (60 * start_hour + start_min)) |
                                                                 ((60 * load_profile.index.hour + load_profile.index.minute)
                                                                  < (60 * end_hour + end_min))), ti,
                                                                time_ind)
                    if this_part['Weekend']:
                        if start_hour <= end_hour:
                            time_ind = np.where((load_profile.index.weekday >= 5) &
                                                                (load_profile.index.month.isin(this_part['Month'])) &
                                                                (((60 * load_profile.index.hour + load_profile.index.minute)
                                                                  >= (60 * start_hour + start_min)) &
                                                                 ((60 * load_profile.index.hour + load_profile.index.minute)
                                                                  < (60 * end_hour + end_min))), ti,
                                                                time_ind)
                        else:
                            time_ind = np.where((load_profile.index.weekday >= 5) &
                                                                (load_profile.index.month.isin(this_part['Month'])) &
                                                                (((60 * load_profile.index.hour + load_profile.index.minute)
                                                                  >= (60 * start_hour + start_min)) |
                                                                 ((60 * load_profile.index.hour + load_profile.index.minute)
                                                                  < (60 * end_hour + end_min))), ti,
                                                                time_ind)
                load_profile_TI[k] = load_profile.loc[time_ind == ti, :].sum()
                load_profile_TI_Charge[k] = this_part['Value'] * load_profile_TI[k]
            Results[TarComp,'EnergyCharge'] = load_profile_TI_Charge.sum(axis=1)
            if 'Discount (%)' in tariff:
                Results[TarComp,'EnergyCharge_Discounted'] = Results[TarComp,'EnergyCharge'] * (1 - tariff['Discount (%)'] / 100)
            else:
                Results[TarComp,'EnergyCharge_Discounted'] = Results[TarComp,'EnergyCharge']
            if 'FiT' in TarCompVal:
                Results[TarComp, 'Fit_Rebate'] = Results['Annual_kWh_exp'] * TarCompVal['FiT']['Value']
            else:
                Results[TarComp, 'Fit_Rebate'] = 0
        if tariff['ProviderType'] == 'Retailer':
            Results['Bill'] = Results['Retailer','DailyCharge'] + Results['Retailer','EnergyCharge_Discounted'] - Results['Retailer','Fit_Rebate']
        else:
            Results['Bill'] = Results['NUOS','DailyCharge'] + Results['NUOS','EnergyCharge_Discounted'] - Results['NUOS','Fit_Rebate']

        print(time.time() - t0)

        return Results

    def demand_charge(load_profile, tariff):


        f_load_profile = load_profile
        imports = [np.nansum(f_load_profile[col].values[f_load_profile[col].values > 0])
                   for col in f_load_profile.columns if col != 'READING_DATETIME']
        Results = pd.DataFrame(index=[col for col in f_load_profile.columns if col != 'READING_DATETIME'],
                               data=imports, columns=['Annual_kWh'])

        Results['Annual_kWh_exp'] = [-1 * np.nansum(f_load_profile[col].values[f_load_profile[col].values < 0])
                                     for col in f_load_profile.columns if col != 'READING_DATETIME']
        if tariff['ProviderType'] == 'Retailer':
            tariff_temp = tariff.copy()
            del tariff_temp['Parameters']
            tariff_temp['Parameters'] = {'Retailer': tariff['Parameters']}
            tariff = tariff_temp.copy()
        for TarComp, TarCompVal in tariff['Parameters'].items():
            Results[TarComp, 'DailyCharge'] = len(load_profile.index.normalize().unique()) * TarCompVal['Daily'][
                'Value']
            if ('Unit', '$/kWh') in TarCompVal['Energy'].items():
                Results[TarComp, 'EnergyCharge'] = Results['Annual_kWh'] * TarCompVal['Energy']['Value']
            else:
                load_profile_imp = load_profile.clip_lower(0)
                load_profile_Q1 = load_profile_imp.loc[load_profile_imp.index.month.isin([1, 2, 3]), :]
                load_profile_Q2 = load_profile_imp.loc[load_profile_imp.index.month.isin([4, 5, 6]), :]
                load_profile_Q3 = load_profile_imp.loc[load_profile_imp.index.month.isin([7, 8, 9]), :]
                load_profile_Q4 = load_profile_imp.loc[load_profile_imp.index.month.isin([10, 11, 12]), :]
                Results['Q1_kWh'] = load_profile_Q1.sum()
                Results['Q2_kWh'] = load_profile_Q2.sum()
                Results['Q3_kWh'] = load_profile_Q3.sum()
                Results['Q4_kWh'] = load_profile_Q4.sum()
                for i in range(1, 5):
                    BlockUse = Results[['Q{}_kWh'.format(i)]].copy()
                    BlockUseCharge = BlockUse.copy()
                    lim = 0
                    for k, v in TarCompVal['Energy'].items():
                        BlockUse[k] = BlockUse['Q{}_kWh'.format(i)]
                        BlockUse[k][BlockUse[k] > v['HighBound']] = v['HighBound']
                        BlockUse[k] = BlockUse[k] - lim
                        BlockUse[k][BlockUse[k] < 0] = 0
                        lim = v['HighBound']
                        BlockUseCharge[k] = BlockUse[k] * v['Value']
                    del BlockUse['Q{}_kWh'.format(i)]
                    del BlockUseCharge['Q{}_kWh'.format(i)]
                    Results[TarComp, 'EnergyCharge_Q{}'.format(i)] = BlockUseCharge.sum(axis=1)
                Results[TarComp, 'EnergyCharge'] = Results[TarComp, 'EnergyCharge_Q1'] + Results[TarComp, 'EnergyCharge_Q2'] \
                                                   + Results[TarComp, 'EnergyCharge_Q3'] + Results[
                                                       TarComp, 'EnergyCharge_Q4']
            if 'Discount (%)' in tariff:
                Results[TarComp, 'EnergyCharge_Discounted'] = Results[TarComp, 'EnergyCharge'] * (
                        1 - tariff['Discount (%)'] / 100)
            else:
                Results[TarComp, 'EnergyCharge_Discounted'] = Results[TarComp, 'EnergyCharge']
            if 'FiT' in TarCompVal:
                Results[TarComp, 'Fit_Rebate'] = Results['Annual_kWh_exp'] * TarCompVal['FiT']['Value']
            else:
                Results[TarComp, 'Fit_Rebate'] = 0
            Results[TarComp, 'Demand'] = 0
            Results[TarComp, 'DemandCharge'] = 0
            for DemCharComp, DemCharCompVal in TarCompVal['Demand'].items():

                TSNum = DemCharCompVal['Demand Window Length']   # number of timestamp
                NumofPeaks = DemCharCompVal['Number of Peaks']

                if TSNum > 1:
                    load_profile_r = load_profile.rolling(TSNum, min_periods=1).mean()
                else:
                    load_profile_r = load_profile
                time_ind = np.zeros(load_profile.shape[0])
                ti = 1
                for k2, v2, in DemCharCompVal['TimeIntervals'].items():
                    start_hour = int(v2[0][0:2])
                    if start_hour == 24:
                        start_hour = 0
                    start_min = int(v2[0][3:5])
                    end_hour = int(v2[1][0:2])
                    if end_hour == 0:
                        end_hour = 24
                    end_min = int(v2[1][3:5])
                    if DemCharCompVal['Weekday']:
                        if start_hour <= end_hour:
                            time_ind = np.where((load_profile.index.weekday < 5) &
                                                (load_profile.index.month.isin(DemCharCompVal['Month'])) &
                                                (((60 * load_profile.index.hour + load_profile.index.minute)
                                                  >= (60 * start_hour + start_min)) &
                                                 ((60 * load_profile.index.hour + load_profile.index.minute)
                                                  < (60 * end_hour + end_min))), ti,
                                                time_ind)
                        else:
                            time_ind = np.where((load_profile.index.weekday < 5) &
                                                (load_profile.index.month.isin(DemCharCompVal['Month'])) &
                                                (((60 * load_profile.index.hour + load_profile.index.minute)
                                                  >= (60 * start_hour + start_min)) |
                                                 ((60 * load_profile.index.hour + load_profile.index.minute)
                                                  < (60 * end_hour + end_min))), ti,
                                                time_ind)
                    if DemCharCompVal['Weekend']:
                        if start_hour <= end_hour:
                            time_ind = np.where((load_profile.index.weekday >= 5) &
                                                (load_profile.index.month.isin(DemCharCompVal['Month'])) &
                                                (((60 * load_profile.index.hour + load_profile.index.minute)
                                                  >= (60 * start_hour + start_min)) &
                                                 ((60 * load_profile.index.hour + load_profile.index.minute)
                                                  < (60 * end_hour + end_min))), ti,
                                                time_ind)
                        else:
                            time_ind = np.where((load_profile.index.weekday >= 5) &
                                                (load_profile.index.month.isin(DemCharCompVal['Month'])) &
                                                (((60 * load_profile.index.hour + load_profile.index.minute)
                                                  >= (60 * start_hour + start_min)) |
                                                 ((60 * load_profile.index.hour + load_profile.index.minute)
                                                  < (60 * end_hour + end_min))), ti,
                                                time_ind)

                load_profile_r = load_profile_r.loc[time_ind == ti, :]
                load_profile_f = load_profile_r.copy()
                load_profile_f = load_profile_f.reset_index()
                load_profile_f = pd.melt(load_profile_f, id_vars=['READING_DATETIME'],
                                         value_vars=[x for x in load_profile_f.columns if x != 'READING_DATETIME'])
                load_profile_f = load_profile_f.rename(columns={'variable': 'HomeID', 'value': 'kWh'})
                load_profile_f['Month'] = pd.to_datetime(load_profile_f['READING_DATETIME']).dt.month

                AveragePeaks = 2 * load_profile_f[['HomeID', 'kWh', 'Month']].groupby(['HomeID', 'Month']).apply(
                    lambda x: x.sort_values('kWh', ascending=False)[:NumofPeaks]).reset_index(drop=True).groupby(
                    ['HomeID']).mean()
                Results[TarComp, 'Demand'] = Results[TarComp, 'Demand'] + AveragePeaks['kWh']
                Results[TarComp, 'DemandCharge'] = Results[TarComp, 'DemandCharge'] + AveragePeaks['kWh'] * DemCharCompVal['Value']
                # AllAveragePeaks = AllAveragePeaks.append(AveragePeaks)


        if tariff['ProviderType'] == 'Retailer':
            Results['Bill'] = Results['Retailer', 'DailyCharge'] + Results['Retailer', 'EnergyCharge_Discounted'] + \
                              Results['NUOS', 'DemandCharge'] - Results['Retailer', 'Fit_Rebate']
        else:
            Results['Bill'] = Results['NUOS', 'DailyCharge'] + Results['NUOS', 'EnergyCharge_Discounted'] + \
                              Results['NUOS', 'DemandCharge'] - Results['NUOS', 'Fit_Rebate']
        return Results

    # Checking the type and run the appropriate function
    if tariff['Type'] == 'Flat_rate':
        Results = fr_calc(load_profile, tariff)
    elif tariff['Type'] == 'TOU':
        Results = tou_calc(load_profile, tariff)
    elif tariff['Type'] == 'Block_Annual':
        Results = block_annual(load_profile, tariff)
    elif tariff['Type'] == 'Block_Quarterly':
        Results = block_quarterly(load_profile, tariff)
    elif tariff['Type'] == 'Demand_Charge':
        Results = demand_charge(load_profile, tariff)
    else:
        Results = 'Error'
    return Results

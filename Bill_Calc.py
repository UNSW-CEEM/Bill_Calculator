import numpy as np
import pandas as pd
import time


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

        Results = pd.DataFrame(load_profile[load_profile > 0].sum(), columns=['Annual_kWh'])
        Results['Annual_kWh_exp'] = -1 * load_profile[load_profile < 0].sum()
        Results['DailyCharge'] = len(load_profile.index.normalize().unique()) * tariff['Parameters']['Daily']['Value']
        Results['EnergyCharge'] = Results['Annual_kWh'] * tariff['Parameters']['Energy']['Value']
        Results['EnergyCharge_Discounted'] = Results['EnergyCharge'] * (1 - tariff['Discount (%)'] / 100)
        Results['Fit_Rebate'] = Results['Annual_kWh_exp'] * tariff['Parameters']['FiT']['Value']
        Results['Bill'] = Results['DailyCharge'] + Results['EnergyCharge'] + Results['Fit_Rebate']

        return Results

    def tou_calc(load_profile, tariff):
        t0 = time.time()
        # Results = pd.DataFrame(load_profile[load_profile > 0].sum(), columns=['Annual_kWh'])
        # Results['Annual_kWh_exp'] = -1 * load_profile[load_profile < 0].sum()

        f_load_profile = load_profile
        imports = [np.nansum(f_load_profile[col].values[f_load_profile[col].values > 0])
                   for col in f_load_profile.columns if col != 'READING_DATETIME']
        Results = pd.DataFrame(index=[col for col in f_load_profile.columns if col != 'READING_DATETIME'],
                               data=imports, columns=['Annual_kWh'])
        Results['Annual_kWh_exp'] = [-1 * np.nansum(f_load_profile[col].values[f_load_profile[col].values < 0])
                                     for col in f_load_profile.columns if col != 'READING_DATETIME']

        load_profile['time_ind'] = 0
        Results['DailyCharge'] = len(load_profile.index.normalize().unique()) * tariff['Parameters']['Daily']['Value']

        load_profile_TI = pd.DataFrame()
        load_profile_TI_Charge = pd.DataFrame()
        ti = 0
        for k, v in tariff['Parameters']['Energy'].items():
            this_part = tariff['Parameters']['Energy'][k].copy()
            ti += 1
            for k2, v2, in this_part['TimeIntervals'].items():
                start_hour = int(this_part['TimeIntervals'][k2][0][0:2])
                if start_hour == 24:
                    start_hour = 0
                start_min = int(this_part['TimeIntervals'][k2][0][3:5])
                end_hour = int(this_part['TimeIntervals'][k2][1][0:2])
                if end_hour == 0:
                    end_hour = 24
                end_min = int(this_part['TimeIntervals'][k2][1][3:5])
                if this_part['Weekday']:
                    if start_hour <= end_hour:
                        load_profile['time_ind'] = np.where((load_profile.index.weekday < 5) &
                                                            (load_profile.index.month.isin(this_part['Month'])) &
                                                            (((60 * load_profile.index.hour + load_profile.index.minute)
                                                              >= (60 * start_hour + start_min)) &
                                                             ((60 * load_profile.index.hour + load_profile.index.minute)
                                                              < (60 * end_hour + end_min))), ti,
                                                            load_profile['time_ind'])
                    else:
                        load_profile['time_ind'] = np.where((load_profile.index.weekday < 5) &
                                                            (load_profile.index.month.isin(this_part['Month'])) &
                                                            (((60 * load_profile.index.hour + load_profile.index.minute)
                                                              >= (60 * start_hour + start_min)) |
                                                             ((60 * load_profile.index.hour + load_profile.index.minute)
                                                              < (60 * end_hour + end_min))), ti,
                                                            load_profile['time_ind'])
                if this_part['Weekend']:
                    if start_hour <= end_hour:
                        load_profile['time_ind'] = np.where((load_profile.index.weekday >= 5) &
                                                            (load_profile.index.month.isin(this_part['Month'])) &
                                                            (((60 * load_profile.index.hour + load_profile.index.minute)
                                                              >= (60 * start_hour + start_min)) &
                                                             ((60 * load_profile.index.hour + load_profile.index.minute)
                                                              < (60 * end_hour + end_min))), ti,
                                                            load_profile['time_ind'])
                    else:
                        load_profile['time_ind'] = np.where((load_profile.index.weekday >= 5) &
                                                            (load_profile.index.month.isin(this_part['Month'])) &
                                                            (((60 * load_profile.index.hour + load_profile.index.minute)
                                                              >= (60 * start_hour + start_min)) |
                                                             ((60 * load_profile.index.hour + load_profile.index.minute)
                                                              < (60 * end_hour + end_min))), ti,
                                                            load_profile['time_ind'])

            load_profile_TI[k] = load_profile.loc[load_profile['time_ind'] == ti, :].sum()
            load_profile_TI_Charge[k] = this_part['Value'] * load_profile_TI[k]

        Results['EnergyCharge'] = load_profile_TI_Charge.sum(axis=1)
        Results['EnergyCharge_Discounted'] = Results['EnergyCharge'] * (1 - tariff['Discount (%)'] / 100)

        Results['Fit_Rebate'] = Results['Annual_kWh_exp'] * tariff['Parameters']['FiT']['Value']
        Results['Bill'] = Results['DailyCharge'] + Results['EnergyCharge'] + Results['Fit_Rebate']
        print(time.time() - t0)

        return Results

    # Checking the type and run the appropriate function
    if tariff['Type'] == 'Flat_rate':
        Results = fr_calc(load_profile, tariff)
    elif tariff['Type'] == 'TOU':

        Results = tou_calc(load_profile, tariff)
    else:
        Results = 'Error'

    return Results

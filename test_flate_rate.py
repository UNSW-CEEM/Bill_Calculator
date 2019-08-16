import unittest
import Bill_Calc
import pandas as pd


class TestFlatRate(unittest.TestCase):
    def setUp(self):
        self.test_profiles = pd.read_csv('test_data/TestLoadProfiles.csv')
        self.test_profiles['Datetime'] = pd.to_datetime(self.test_profiles['Datetime'])
        self.test_profiles = self.test_profiles.set_index('Datetime')
        self.just_daily_charge = {'Date_accessed': '2018',
                                  'Discount (%)': 0, 'Distributor': 'Essential Energy',
                                  'Name': 'Essential Energy TOU NSW 2017/18',
                                  'Parameters': {'Daily': {'Unit': '$/day', 'Value': 0.8568},
                                                 'Energy': {'Unit': '$/kWh', 'Value': 0.0}},
                                  'Provider': 'Essential Energy', 'ProviderType': 'Retailer', 'State': 'NSW',
                                  'Tariff ID': 'TN0028', 'Type': 'Flat_rate'}

    def test_has_expected_columns(self):
        profile_with_no_consumption = self.test_profiles.loc[:, ['no_consumption']]
        bill = Bill_Calc.bill_calculator(profile_with_no_consumption, self.just_daily_charge, FiT=False)
        expected_columns = ['Annual_kWh', 'Retailer_DailyCharge', 'Retailer_EnergyCharge',
                            'Retailer_EnergyCharge_Discounted', 'Retailer_Fit_Rebate', 'Bill']
        self.assertEqual(list(bill.columns), expected_columns, "flat rate results does not have expected columns")
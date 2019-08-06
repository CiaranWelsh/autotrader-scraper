import pandas as pd
import numpy as np
import os, glob
import re

WORKING_DIRECTORY = os.path.join(os.path.dirname(os.path.dirname(__file__)))
DATA_DIR = os.path.join(WORKING_DIRECTORY, 'data')
CARS_DATA_RAW = os.path.join(DATA_DIR, 'preprocessing_test_data_do_not_modify.csv')


class PreprocessData:

    def __init__(self, data):
        self.data = data
        self.title_data = self.data['title']
        self.extra_infomation = self.data['num_owners_from_new_text']

    def _extract_make(self):
        dct = {}
        for i in range(len(self.title_data)):
            dct[i] = self.title_data.iloc[i].split(' ')[0]
        return dct

    def _extract_model(self):
        dct = {}
        for i in range(len(self.title_data)):
            dct[i] = self.title_data.iloc[i].split(' ')[1]
        return dct

    def _extract_engine_size(self):
        dct = {}
        for i in range(len(self.title_data)):
            s = re.findall('\s(\d\.\d)\s', self.title_data.iloc[i])
            if len(s) == 1:
                s = s[0]
            else:
                s = np.nan
            dct[i] = float(s)
        return dct

    def _extract_number_of_doors(self):
        dct = {}
        for i in range(len(self.title_data)):
            dr = re.findall('\ddr', self.title_data.iloc[i])
            if len(dr) == 1:
                dr = dr[0]
            else:
                dr = np.nan
            dct[i] = dr
        return dct

    def _extract_service_history(self):
        dct = {}
        for i in range(len(self.extra_infomation)):
            string = str(self.extra_infomation.iloc[i]).lower()
            service = re.findall('service history', string)
            if len(service) == 1:
                service = service[0]
            else:
                service = np.nan
            dct[i] = service

        return dct

    def _extract_mot(self):
        dct = {}
        for i in range(len(self.extra_infomation)):
            string = str(self.extra_infomation.iloc[i]).lower()
            service = re.findall('mot', string)
            if len(service) == 1:
                service = service[0]
            else:
                service = np.nan
            dct[i] = service

        return dct

    def _extract_insurance(self):
        dct = {}
        for i in range(len(self.extra_infomation)):
            string = str(self.extra_infomation.iloc[i]).lower()
            service = re.findall('insurance', string)
            if len(service) == 1:
                service = service[0]
            else:
                service = np.nan
            dct[i] = service

        return dct

    def extract_all(self):
        dct = {
            'model': self._extract_model(),
            'make': self._extract_make(),
            'service_history': self._extract_service_history(),
            'mot': self._extract_mot(),
            'insurance': self._extract_insurance(),
        }
        pd_dct = {}
        for k, v in dct.items():
            pd_dct[k] = pd.Series(v)
        df = pd.concat(pd_dct, axis=1)
        return pd.concat([df, self.data], axis=1)


if __name__ == '__main__':
    data = pd.read_csv(CARS_DATA_RAW, index_col=0)
    x = PreprocessData(data)
    y = x.extract_all()
    fname = os.path.join(DATA_DIR, 'preprocessed_data.csv')
    y.to_csv(fname)

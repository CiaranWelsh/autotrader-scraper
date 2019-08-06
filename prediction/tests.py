import unittest
from collections import Counter

from .preprocessing import *


class PreprocessingTests(unittest.TestCase):

    def setUp(self) -> None:
        self.data = pd.read_csv(CARS_DATA_RAW, index_col=0)

    def test_extract_make(self):
        x = PreprocessData(self.data)
        makes = x._extract_make()
        count_data = Counter(makes.values())
        self.assertEqual(258, count_data['Vauxhall'])

    def test_extract_model(self):
        x = PreprocessData(self.data)
        makes = x._extract_model()
        count_data = Counter(makes.values())
        self.assertEqual(78, count_data['Astra'])

    def test_extract_engine_size(self):
        x = PreprocessData(self.data)
        s = x._extract_engine_size()
        count = Counter(s.values())
        self.assertEqual(1158, count[1.4])

    def test_extract_number_of_doors(self):
        x = PreprocessData(self.data)
        x._extract_number_of_doors()

    def test_extract_service_history(self):
        x = PreprocessData(self.data)
        his = x._extract_service_history()
        count = Counter(his.values())
        self.assertEqual(134, count['service history'])

    def test_extract_all(self):
        x = PreprocessData(self.data)
        print(x.extract_all())


if __name__ == '__main__':
    unittest.main()

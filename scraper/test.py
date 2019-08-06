import unittest
from bs4 import BeautifulSoup

from .scraper import *

class ScraperTests(unittest.TestCase):

    def setUp(self) -> None:
        self.kwargs = {
            'sort': 'distance',
            'postcode': 'ne46an',
            'price-to': 4000,
            'minimum-badge-engine-size': '1.4',
            'maximum-badge-engine-size': '1.4',
            # 'make': 'CHEVROLET'
        }

    def test_get_page(self):
        s = Scraper(max_pages=3, **self.kwargs)
        self.assertIsInstance(s.soup, BeautifulSoup)

    def test_num_cars_found(self):
        s = Scraper(max_pages=3, **self.kwargs)
        self.assertIsInstance(len(s), int) # actual number associated with search will change often

    def test_url_is_built(self):
        s = Scraper(max_pages=3, **self.kwargs)
        expected = 'https://www.autotrader.co.uk/car-search?sort=distance&price-to=4000&minimum-badge-engine-size=1.4&maximum-badge-engine-size=1.4'
        self.assertEqual(expected, s.search_url)

    def test_num_items_per_page(self):
        s = Scraper(max_pages=3, **self.kwargs)
        self.assertEqual(13, s._num_items_per_page())

    def test_num_pages(self):
        s = Scraper(max_pages=3, **self.kwargs)
        self.assertEqual(758, s._number_of_pages())

    def test_scrape1page(self):
        s = Scraper(max_pages=2, **self.kwargs)
        self.assertIsInstance(s.scrape(), pd.DataFrame)

    def test_iter(self):
        s = Scraper(max_pages=2, **self.kwargs)
        expected = [1, 2]
        nums = []
        for i in s:
            nums.append(i)
        self.assertEqual(expected, nums)

    def test(self):
        s = Scraper(**self.kwargs)
        print(len(s))
        s.scrape()
        # for i in s:
        #     response = s._response(i)
        #     print(response.url)
        #     print(i.search_url)









if __name__ == '__main__':
    unittest.main()
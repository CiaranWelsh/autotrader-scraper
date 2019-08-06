import os, glob
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import requests
import re
import urllib3
from time import sleep
from copy import deepcopy
from collections import OrderedDict

# todo ensure that given url is an autotrader website
# todo write a wrapper around requests that can query the api directly
# todo write second read information for second format of car item
# todo tell user when there are no cars in the search
# todo add all makes and models to the valid kwargs dict. This is time consuming so left to user
#  to give accurate values for these searches
# todo Retrieve number of cars in search

class Scraper:
    url = 'https://www.autotrader.co.uk/car-search'

    def __init__(self, max_pages=None, use_cache=False, sleep_time_mu=0.2,
                 sleep_time_sigma=0.05, output_fname=None,
                 start_page=1, **kwargs):
        self.max_pages = max_pages
        self.start_page = start_page
        self.use_cache = use_cache
        self.sleep_time_mu = sleep_time_mu
        self.sleep_time_sigma = sleep_time_sigma
        self.output_fname = output_fname
        self.kwargs = kwargs

        self._reached_max = False

        # current page.
        self._page = self.start_page
        # response and soup for first page
        self.response = self._response(self.start_page)
        self.soup = self._soup(self.response)

        # set maximum number of pages to all if max pages not specified
        if self.max_pages is None:
            self.max_pages = self._number_of_pages()

        if self.max_pages > self._number_of_pages():
            raise ValueError('The maximum number of pages is {}'.format(self._number_of_pages()))

        # place to store results
        if self.output_fname is None:
            self.output_fname = os.path.join(os.path.abspath(''), 'preprocessing_test_data_do_not_modify.csv')

        # place to store cached data
        self.cache_file = os.path.join(os.path.dirname(self.output_fname), '.autotrader_scraper_cache.txt')

        # self.scrape()

    def __len__(self):
        return self._get_number_of_cars_found()

    def __iter__(self):
        return self

    def __next__(self):
        if self._page > self.max_pages:
            raise StopIteration
        self._page += 1
        return self._page - 1

    def scrape(self):
        lst = []
        for page in self:
            if self._reached_max:
                break
            self.response = self._response(page)
            print('scraping page {} of {}: {}'.format(page, self.max_pages, self.response.url))
            self.soup = self._soup(self.response)
            random_sleep_time = np.random.normal(self.sleep_time_mu, self.sleep_time_sigma)
            sleep(random_sleep_time)
            scraped = self._scrape_page()
            lst += scraped

        df = pd.DataFrame(lst)
        df = df.drop_duplicates()

        df.to_csv(self.output_fname)
        with open(self.cache_file, 'w') as f:
            f.write(str(self._page))
        print('data has been saved to "{}"'.format(self.output_fname))
        return df

    def _response(self, page):
        self.kwargs['page'] = page
        return requests.get(url=self.url, params=self.kwargs)

    @property
    def search_url(self):
        return self.response.url

    def _soup(self, response):
        return BeautifulSoup(response.content, features='lxml')

    def _get_number_of_cars_found(self):
        cars_found = self.soup.select('div.search-form div > h1')[0].text
        cars_found = re.findall('(\A[\d,]*)|(\A\d+)', cars_found)
        assert len(cars_found) == 1
        cars_found = cars_found[0][0].replace(',', '')
        if cars_found == 0:
            raise ValueError('No cars found. Please widen search parameters and ensure spelling accuracy')
        return int(cars_found)

    def _num_items_per_page(self):
        articles = self.soup.select('article')
        return len(articles)

    def _number_of_pages(self):
        num_pages = len(self) // self._num_items_per_page()
        remainder = len(self) % self._num_items_per_page()
        if remainder > 1:
            num_pages += 1
        return num_pages

    def _scrape_page(self):
        lst = []
        articles = self.soup.select('article')
        if articles == []:
            print('Maximum displayed results reached - Please refine your search to see different results.')
            self._reached_max = True
            return []
        for i in range(len(articles)):
            try:
                # lst.append(self._scrape1article(articles[i]))
                info = self._scrape_information(articles[i])
                lst.append(info)
            except ValueError:
                continue
            except IndexError:
                continue
        return lst

    def _scrape_price(self, article):
        div = article.select('.price-column div.vehicle-price')
        if len(div) != 1:
            raise ValueError('div is not of length 1. Got {}'.format(len(div)))
        price = float(div[0].text.replace(',', '').replace('£', ''))
        return price

    def _scrape_information(self, article):
        div = article.select('.content-column > div')
        if len(div) != 1:
            raise ValueError
        div = div[0]
        title = div.select('h2 > a')[0].text
        link = div.select('h2 > a')[0]['href']
        num_owners_from_new = div.select('p.listing-attention-grabber')
        assert len(num_owners_from_new) == 1
        num_owners_from_new_text = num_owners_from_new[0].text
        specs = div.select('ul.listing-key-specs')
        assert len(specs) == 1
        specs = specs[0]
        specs = specs.select('li')
        reg = specs[0].text
        car_type = specs[1].text
        miles = specs[2].text.replace(',', '')
        miles = int(re.findall('(\d*)', miles)[0])
        eng = specs[3].text
        bhp = specs[4].text
        gears = specs[5].text
        fuel = specs[6].text
        extra_detail = div.select('ul.listing-extra-detail > li')
        if len(extra_detail) != 0:
            extra_detail = extra_detail[0].text
        else:
            extra_detail = np.nan
        seller = div.select('div > div.seller-type')
        seller_type = seller[0].text
        seller_loc = div.select('div.seller-location')[0]
        distance = seller_loc.text
        seller_town = seller_loc.select('span')[0].text

        return OrderedDict(
            title=title,
            price=self._scrape_price(article),
            num_owners_from_new_text=num_owners_from_new_text,
            reg=reg,
            car_type=car_type,
            miles=miles,
            eng=eng,
            bhp=bhp,
            gears=gears,
            fuel=fuel,
            extra_detail=extra_detail,
            seller_type=seller_type,
            distance=distance,
            seller_town=seller_town,
            link=link,
        )


if __name__ == '__main__':
    kwargs = {
        'sort': 'distance',
        'postcode': 'ne46an',
        'price-to': 4000,
        'minimum-badge-engine-size': '1.4',
        'maximum-badge-engine-size': '1.4'
    }

    s = Scraper(use_cache=False, max_pages=3, **kwargs)




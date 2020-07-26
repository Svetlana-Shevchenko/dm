import requests
import bs4
import re

from pymongo import MongoClient
from typing import List, Dict

resources = {
    'hh': {
        'name': 'HeadHunter',
        'pagination': 'https://hh.ru/search/vacancy?area=1',
        'pages': 'https://hh.ru/search/vacancy?L_is_autosearch=false&area=1&clusters=true&enable_snippets=true&page=',
        'headers': {
            'User-Agent': 'curl/7.54.0'
        },
        'domain': 'https://hh.ru'
    },

    'sj': {
        'name': 'SuperJob',
        'pagination': 'https://www.superjob.ru/vacancy/search/',
        'pages': 'https://www.superjob.ru/vacancy/search/?page=',
        'headers': {
            'User-Agent': 'curl/7.54.0'
        },
        'domain': 'https://www.superjob.ru'
    }
}


class Pagination:

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

        self.__bs = self._get_main_page()

    def _get_main_page(self) -> bs4.BeautifulSoup:
        return bs4.BeautifulSoup(requests.get(self.pagination, headers=self.headers).text, 'html.parser')


class HHPagination(Pagination):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def pagination_links(self) -> List[str]:
        return [self.pages + str(x) for x in  # COMMENT -->  !!
                range(1, 5)]

        # DELETE PREV "RETURN" FOR FULL PARSE WORKING
        return [self.pages + str(x) for x in
                range(1, int(self._Pagination__bs.select('a[data-qa="pager-page"]')[-1].text) + 1)]


class SJPagination(Pagination):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def pagination_links(self) -> List[str]:
        return [self.pages + str(x) for x in  # COMMENT -->  !!
                range(1, 5)]

        # DELETE PREV "RETURN" FOR FULL PARSE WORKING
        return [self.pages + str(x) for x in
                range(1, int(self._Pagination__bs.select('.f-test-button-100 ._3IDf-')[0].text))]


class Job:

    def __init__(self, pagination: Pagination, client: MongoClient):
        self.__links = pagination.pagination_links
        self.headers = pagination.headers
        self.domain = pagination.domain
        self.client = client

    #        self.jobs = pagination.jobs if 'jobs' in list(vars(pagination).keys()) else False

    def _get_content_from_links(self, link: str) -> bs4.BeautifulSoup:
        return bs4.BeautifulSoup(requests.get(link, headers=self.headers).text, 'html.parser')

    def _check_job(self, link: str) -> bool:
        return self.client.jobs.find_one({'job-link': link}) is None

    @property
    def jobs(self) -> List:
        return [self.render_job(self._get_content_from_links(link)) for link in self._Job__links]

    def save_job(self, job: Dict) -> Dict:
        if self._check_job(job['job-link']):
            self.client.jobs.insert_one(job)
        return job


class HHJob(Job):

    def __init__(self, pagination: Pagination, client: MongoClient):
        super().__init__(pagination, client)

    def render_job(self, bs: bs4.BeautifulSoup) -> Dict:
        result = {}
        for x in bs.select('.vacancy-serp-item'):
            result = {
                'job-name': x.select('a[data-qa="vacancy-serp__vacancy-title"]')[0].text,
                'job-link': x.select('a[data-qa="vacancy-serp__vacancy-title"]')[0]['href'],
                'city': x.select('span[data-qa="vacancy-serp__vacancy-address"]')[0].text,
                'description': x.select('div[data-qa="vacancy-serp__vacancy_snippet_responsibility"]')[0].text,
                'requires': x.select('div[data-qa="vacancy-serp__vacancy_snippet_requirement"]')[0].text,
            }

            try:
                result['prices'] = x.select('span[data-qa="vacancy-serp__vacancy-compensation"]')[0].text. \
                    replace('\xa0', '').replace('руб.', ''). \
                    replace('от', '').replace('до', '').replace('/месяц', '').strip().split(
                    '-')  # @TODO 5 min for regexp replace!!
                result['job-company'] = x.select('a[data-qa="vacancy-serp__vacancy-employer"]')[0].text
                result['images'] = [x['src'] for x in x.select('img.vacancy-serp-item__logo')]
            except IndexError:

                pass

        return self.save_job(result)


class SJJob(Job):

    def __init__(self, pagination: Pagination, client: MongoClient):
        super().__init__(pagination, client)

    def render_job(self, bs: bs4.BeautifulSoup) -> Dict:
        result = {}
        for x in bs.select('.f-test-vacancy-item'):
            result = {
                'job-name': x.select('.icMQ_')[0].text,
                'job-link': self.domain + x.select('.icMQ_')[0]['href'],
            }

            try:
                result['prices'] = x.select('.f-test-text-company-item-salary')[0].text. \
                    replace('\xa0', '').replace('руб.', ''). \
                    replace('от', '').replace('до', '').replace('/месяц', '').strip().split(
                    '—')  # @TODO 5 min for regexp replace!!
                result['job-company'] = x.select('.f-test-text-vacancy-item-company-name')[0].text
                result['city'] = x.select('.f-test-text-company-item-location span')[2].text

                desc_req = str(x.select('.HSTPm span')[0]).split('<br/>')

                result['description'] = re.search('>(.*)', desc_req[0]).group(1)
                result['requires'] = re.search('(.*)(</span>).*', desc_req[1]).group(1)
                result['images'] = [x['src'] for x in x.select('img')]

            except IndexError:

                pass

        return self.save_job(result)


class JobsHub:

    def __init__(self, structure: dict, client: MongoClient):
        self.name = structure['name']

        if structure['name'] == 'HeadHunter':
            self.pagination = HHPagination(**structure)
            self.job_generator = HHJob(self.pagination, client)
        elif structure['name'] == 'SuperJob':
            self.pagination = SJPagination(**structure)
            self.job_generator = SJJob(self.pagination, client)

        self.jobs = self.job_generator.jobs


if __name__ == '__main__':
    ####### NOT DONE YET, till sunday 27.07
    jobs = {key: JobsHub(resources[key], MongoClient('172.22.200.92', 27017)['jobs']) for key in resources}

    try:
        [print(x) for x in jobs['hh'].job_generator.client.jobs.find(
            {"$and": [{"prices.0": {"$gte": f'{int(input("Write min salary"))}'}}, {"price.0": {"$ne": "По говорённости"}}]})]
    except:
        print('Wrong input')

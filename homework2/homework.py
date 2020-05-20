import requests
import bs4
import re

from typing import List, Dict
import pandas as pd

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

    def __init__(self, pagination: Pagination):
        self.__links = pagination.pagination_links
        self.headers = pagination.headers
        self.domain = pagination.domain
#        self.jobs = pagination.jobs if 'jobs' in list(vars(pagination).keys()) else False

    def _get_content_from_links(self, link: str) -> bs4.BeautifulSoup:
        return bs4.BeautifulSoup(requests.get(link, headers=self.headers).text, 'html.parser')

    @property
    def jobs(self) -> List:
        return [self.render_job(self._get_content_from_links(link)) for link in self._Job__links]


class HHJob(Job):

    def __init__(self, pagination: Pagination):
        super().__init__(pagination)


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
                    replace('от', '').replace('до', '').strip().split('-') #@TODO 5 min for regexp replace!!
                result['job-company'] = x.select('a[data-qa="vacancy-serp__vacancy-employer"]')[0].text

            except IndexError:

                pass

        return result


class SJJob(Job):

    def __init__(self, pagination: Pagination):
        super().__init__(pagination)

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
                    replace('от', '').replace('до', '').strip().split('—') #@TODO 5 min for regexp replace!!
                result['job-company'] = x.select('.f-test-text-vacancy-item-company-name')[0].text
                result['city']= x.select('.f-test-text-company-item-location span')[2].text

                desc_req = str(x.select('.HSTPm span')[0]).split('<br/>')

                result['description'] = re.search('>(.*)' , desc_req[0]).group(1)
                result['requires'] = re.search('(.*)(</span>).*', desc_req[1]).group(1)

            except IndexError:

                pass

        return result

class JobsHub:

    def __init__(self, structure: dict):
        self.name = structure['name']

        if structure['name'] == 'HeadHunter':
            self.pagination = HHPagination(**structure)
            self.job_generator = HHJob(self.pagination)
        elif structure['name'] == 'SuperJob':
            self.pagination = SJPagination(**structure)
            self.job_generator = SJJob(self.pagination)

        self.jobs = self.job_generator.jobs




if __name__ == '__main__':
    jobs = {key: JobsHub(resources[key]) for key in resources}

    # PANDAS WORK: printing AS DATAFRAME
    [print(pd.DataFrame.from_dict(jobs[key].jobs)) for key in jobs]
    # PANDAS WORK: printing AS STRING
    [print(pd.DataFrame.from_dict(jobs[key].jobs).to_string())for key in jobs]

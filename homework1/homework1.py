from copy import copy
import requests
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X x.y; rv:42.0) Gecko/20100101 Firefox/42.0'
}


class Product:
    name = 'NOT NAME'

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

        self.product = self._get_adv_info

    def __str__(self):
        return self.name

    @property
    def _get_adv_info(self):
        try:
            return json.loads(requests.get('https://5ka.ru/api/v2/special_offers/' + str(self.id),
                                           headers=headers).text)['product']
        except json.JSONDecodeError as e:
            print(e)


class CatalogParser:

    def __init__(self, start_url: str, category_url: str):
        self.__start_url: str = start_url
        self.__category_url: str = category_url
        self.__product_list: list = []
        self.__category_list: list = []

    def parse(self):
        url: str = self.__start_url

        if not self.__category_list:
            self.__category_list = self._get_categories

        while url:
            response = requests.get(url, headers=headers)
            data = response.json()
            url = data.get('next')
            self.__product_list.extend([Product(**itm) for itm in data.get('results')])

    @property
    def _get_categories(self):
        try:
            list = json.loads(requests.get(self.__category_url, headers=headers).text)
            return {x['parent_group_code']: {'name': x['parent_group_name'], 'products': [], 'count': 0} for x in list}
        except json.JSONDecodeError as e:
            print(e)

    @property
    def products(self):
        return copy(self.__product_list)

    @property
    def categories(self):
        f_list = copy(self.__category_list)
        for product in self.products:
            for category in f_list:
                if product.product['group']['parent_group_name'] == f_list[category]['name']:
                    f_list[category]['products'].append(product)
                    f_list[category]['count'] = f_list[category]['count'] + 1
        return f_list


if __name__ == '__main__':
    parser = CatalogParser(start_url='https://5ka.ru/api/v2/special_offers/',
                           category_url='https://5ka.ru/api/v2/categories/')
    parser.parse()
    
    for key in parser.categories:
        if key != 'OTHER':
            with open(f'{key}.json', 'w') as file:
                file.write(json.dumps(parser.categories[key]))

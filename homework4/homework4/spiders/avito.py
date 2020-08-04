import scrapy
from pymongo import MongoClient


class AvitoSpider(scrapy.Spider):
    name = 'avito'
    allowed_domains = ['avito.ru']
    start_urls = ['https://www.avito.ru/moskva/kvartiry/prodam']
    pagination_num = 0
    pagination_list_length = 100
    connector = MongoClient('172.22.200.92', 27017).advertisement.adv

    def parse(self, response):
        if self.pagination_num < self.pagination_list_length:
            for i in range(0, self.pagination_list_length):
                self.pagination_num += 1
                response.follow(response.url + f'?p={i}', callback=self.parse)

        for advertisment in response.css('a.js-item-slider.item-slider::attr("href")').extract():
            yield response.follow(advertisment, callback=self.parse_advertisement)

    def parse_advertisement(self, response) -> None:
        return self.connector.insert_one({
            'title': response.css('span.title-info-title-text::text').extract()[0],
            'url': response.url,
            'coast': int(response.css('span.js-item-price:first-of-type::text').extract()[0].replace(' ', '')),
            'description': {
                x.css('span::text').extract()[0].replace(':', ''): x.css('a::text').extract()[0]
                if len(x.css('a::text').extract()) != 0
                else x.css('::text').extract()[2]
                        if len(x.css('::text').extract()) > 2
                    else None
                for x in
                response.css('div.item-view-block li.item-params-list-item')}
        }) and None  # Delete end symbols

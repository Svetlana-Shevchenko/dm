import scrapy

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from homework7.items import Homework7Item
from scrapy.loader import ItemLoader


class ZillowSpider(scrapy.Spider):
    name = 'zillow'
    allowed_domains = ['www.zillow.com']
    start_urls = ['https://www.zillow.com/homes/']

    driver = webdriver.Firefox()

    def __init__(self, region: str, *args, **kwargs):
        self.region = region
        self.start_urls = [self.start_urls[0] + region]
        super().__init__(*args, **kwargs)

    def parse(self, response):
        for url in response.css('a.list-card-link.list-card-img::attr("href")').extract():
            yield response.follow(url, callback=self.parse_block)

    def parse_block(self, response):
        item = ItemLoader(Homework7Item(), response)
        self.driver.get(response.url)
        self.driver.execute_script(
            "document.querySelector('div.ds-media-col.ds-media-col-hidden-mobile').scroll(0,90000)")

        item.add_value('photos', [
            x.get_attribute('srcset').split(',')[-1].strip().split(' ')[0] for x in
            self.driver.find_elements_by_css_selector('ul.media-stream li source[type="image/jpeg"]')
        ])

        item.add_value('address', ' '.join([x.text for x in
                                            self.driver.find_elements_by_css_selector(
                                                'div.ds-data-col div.ds-home-details-chip h1.ds-address-container span')]))

        item.add_value('price',
                       self.driver.find_elements_by_css_selector('div.ds-summary-row-container h3 span.ds-value')[
                           0].text)

        yield item.load_item()


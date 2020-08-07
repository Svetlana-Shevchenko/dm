from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from homework7 import settings
from homework7.spiders.zillow import ZillowSpider

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)
    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(ZillowSpider, 'Bradenton,-FL_rb')
    process.start()

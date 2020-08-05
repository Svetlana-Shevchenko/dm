from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from homework5 import settings
from homework5.spiders.habr import HabrSpider

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)
    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(HabrSpider)
    process.start()

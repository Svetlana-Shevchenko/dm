from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from homework4 import settings
from homework4.spiders.avito import AvitoSpider

if __name__ == '__main__':
    crawl_settings = Settings()
    crawl_settings.setmodule(settings)
    proc = CrawlerProcess(settings=crawl_settings)
    proc.crawl(AvitoSpider)
    proc.start()
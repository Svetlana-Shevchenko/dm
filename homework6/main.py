from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from homework6 import settings
from homework6.spiders.instagram import InstagramSpider

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)
    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(InstagramSpider,
                     'algovrilov',
                     '#PWD_INSTAGRAM_BROWSER:10:1596728963:AeVQALX6vmsD6WkrcewCJgFPBjowNDh9rS+wpInj/BC5ArsIcER6u43s5pfk4YI9Azg1jxr3l+3GcLMp6O1dO8xaiyMO9mlRvdWQzj761qF/cA4QHxtPIji0ZwlIdEwUwO6NJWkX6Co7HifbFoF3K/Vo',
                     ['gefestart'])
    process.start()

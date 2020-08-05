# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import TakeFirst


class authorItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    _id = scrapy.Field()
    author_name = scrapy.Field(output_processor=TakeFirst())
    author_url = scrapy.Field(output_processor=TakeFirst())
    pass


class postItem(scrapy.Item):
    _id = scrapy.Field()
    images = scrapy.Field()
    title = scrapy.Field(output_processor=TakeFirst())
    comments = scrapy.Field(output_processor=TakeFirst())
    author_id = scrapy.Field()
    post_url = scrapy.Field(output_processor=TakeFirst())
    pass

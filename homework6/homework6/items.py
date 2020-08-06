# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst


def clean_photos(values):
    if values[:2] == '//':
        return f'http:{values}'
    return values



class Homework6Item(scrapy.Item):
    _id = scrapy.Field()
    user_name = scrapy.Field(output_processor=TakeFirst())
    user_id = scrapy.Field(output_processor=TakeFirst())
    post_pub_date = scrapy.Field(output_processor=TakeFirst())
    like_count = scrapy.Field(output_processor=TakeFirst())
    photos = scrapy.Field(output_processor=TakeFirst())

# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
import re
from scrapy.loader.processors import TakeFirst, MapCompose, Join

def remove_rnt(value):
    return value.replace("\r",'').replace("\t",'').replace("\n",'')

def concat(value):
    return ''.join(value)

def remove_double_spaces(value):
    return re.sub(' +', ' ', value)

def strip(value):
    return value.strip()

class Ad(scrapy.Item):
    provider = scrapy.Field()
    external_id = scrapy.Field(input_processor=MapCompose(concat, remove_rnt, remove_double_spaces, strip))
    date = scrapy.Field()
    offer = scrapy.Field()
    title = scrapy.Field(input_processor=MapCompose(concat, remove_rnt, remove_double_spaces, strip))
    description = scrapy.Field(input_processor=MapCompose(concat, remove_double_spaces))
    price = scrapy.Field()
    address = scrapy.Field(input_processor=MapCompose(concat, remove_rnt, remove_double_spaces, strip), output_processor=Join(', '))
    lattitude = scrapy.Field()
    longitude = scrapy.Field()
    ext_category = scrapy.Field()
    images = scrapy.Field()
    videos = scrapy.Field()
    site = scrapy.Field()
    details = scrapy.Field()
    author_external_id = scrapy.Field()
    author = scrapy.Field(input_processor=MapCompose(concat, remove_rnt, remove_double_spaces, strip), output_processor=TakeFirst())
    phone = scrapy.Field()
    original_url = scrapy.Field()
    created_at = scrapy.Field()
    processed = scrapy.Field(default=False)
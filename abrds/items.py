# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import TakeFirst, MapCompose, Join

def remove_rnt(value):
	return value.replace("\r",'').replace("\t",'').replace("\n",'')


class Ad(scrapy.Item):
    provider = scrapy.Field()
    external_id = scrapy.Field(input_processor=MapCompose(remove_rnt))
    date = scrapy.Field()
    offer = scrapy.Field()
    title = scrapy.Field()
    description = scrapy.Field()
    price = scrapy.Field()
    address = scrapy.Field(input_processor=MapCompose(remove_rnt))
    lattitude = scrapy.Field()
    longitude = scrapy.Field()
    ext_category = scrapy.Field()
    images = scrapy.Field()
    videos = scrapy.Field()
    site = scrapy.Field()
    details = scrapy.Field()
    author_external_id = scrapy.Field()
    author = scrapy.Field()
    phone = scrapy.Field()
    original_url = scrapy.Field()
    created_at = scrapy.Field()
    processed = scrapy.Field(default=False)
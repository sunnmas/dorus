# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
import re
import datetime
from scrapy.loader.processors import TakeFirst, MapCompose, Join

def remove_rnt(value):
    return value.replace("\r",'').replace("\t",'').replace("\n",'')

def concat(value):
    return ''.join(value)

def remove_double_spaces(value):
    return re.sub('  ', ' ', value)
def remove_spaces(value):
    return re.sub(' ', '', value)

def strip(value):
    return value.strip()

def clean_address(value):
    try:
        shit = re.search("\d+ минут от ", value)[0]
        return value.replace(shit, '')
    except BaseException:
        return value
def clean_price(value):
    try:
        return value.replace("\xa0", '').replace('₽','')
    except BaseException:
        return value

def clean_author_id(value):
    return value.replace('ID ','')

def clean_phone(value):
    return value.replace('+7','')

def clean_date(value):
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    yesterday = (datetime.datetime.today() - datetime.timedelta(1)).strftime('%Y-%m-%d')
    date = value.replace('Сегодня', today)
    date = date.replace('сегодня,', today)
    date = date.replace('Вчера', yesterday)
    date = date.replace('вчера,', yesterday)
    date = date.replace('\xa0',' ')
    return date

class Ad(scrapy.Item):
    provider = scrapy.Field()
    external_id = scrapy.Field(input_processor=MapCompose(concat, remove_rnt, remove_double_spaces, strip))
    date = scrapy.Field(input_processor=MapCompose(clean_date))
    title = scrapy.Field(input_processor=MapCompose(concat, remove_rnt, remove_double_spaces, strip))
    description = scrapy.Field(input_processor=MapCompose(concat, remove_double_spaces), output_processor=TakeFirst())
    price = scrapy.Field(input_processor=MapCompose(concat, remove_rnt, remove_spaces, strip, clean_price))
    address = scrapy.Field(input_processor=MapCompose(concat, remove_rnt, remove_double_spaces, strip, clean_address), output_processor=Join(', '))
    lattitude = scrapy.Field()
    longitude = scrapy.Field()
    category = scrapy.Field()
    images = scrapy.Field()
    videos = scrapy.Field()
    site = scrapy.Field()
    details = scrapy.Field()
    author_external_id = scrapy.Field(input_processor=MapCompose(clean_author_id))
    author = scrapy.Field(input_processor=MapCompose(concat, remove_rnt, remove_double_spaces, strip), output_processor=TakeFirst())
    company = scrapy.Field()
    phone = scrapy.Field(input_processor=MapCompose(clean_phone))
    original_url = scrapy.Field()
    created_at = scrapy.Field()
    processed = scrapy.Field()
    actual = scrapy.Field()
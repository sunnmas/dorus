import scrapy
import re
import requests

class QuotesSpider(scrapy.Spider):
    name = 'dorus'
    start_urls = [
        'http://www.cmlt.ru/ads--rubric-1394'
    ]

    allowed_domains = [
        'cmlt.ru'
    ]

    def parse(self, response):
        # follow links to author pages
        for href in response.xpath('///div[@class="onepost"]//a/@href').getall():
            yield response.follow(href, self.parse_item)
        # follow pagination links
        nextPage = response.xpath('///div[@class="margt24"]/span[@class="link"]/@onclick').get().replace("openLink('",'').replace("', true)",'')
        yield response.follow(nextPage, self.parse)
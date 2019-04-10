# scrapy runspider abrds/spiders/cmlt.py -o cmlt.json

import scrapy
import re
import requests

class QuotesSpider(scrapy.Spider):
    name = 'cmlt'
    start_urls = [
        'https://www.cmlt.ru/ads--rubric-88'
    ]

    allowed_domains = [
        'cmlt.ru'
    ]

    def parse(self, response):
        # follow links to adv pages
        links = response.css('div.item a.an-bg-link::attr(href)').getall()
        links = list(set(links))
        print(links)
        for href in links:
            yield response.follow("https://cmlt.ru"+href, self.parse_item)
        # follow pagination links
        nextPage = "https://cmlt.ru"+response.css('a.pagesController:last-child::attr(href)').get()
        yield response.follow(nextPage, self.parse)


    def parse_item(self, response):
        id = re.search('ad-.\d+',response.url).group(0).replace('ad-', '')
        title = response.css('h1::text').get().replace('\n','')
        description = ''.join(response.css('div.full-an-info div.view-an.content-block::text').getall()).replace('\n','')
        try:
            price = response.css('tr.fullAn-price div::text').get().replace('руб.', '').replace('\n', '').replace('\xa0', '').replace(' ', '')
        except BaseException:
            price = 0
        
        author_url = response.css('div.an-page-other-user-ans a::attr(href)').get()
        print("URL автора: https://cmlt.ru"+author_url)
        r = requests.get('https://cmlt.ru'+author_url).text
        author = re.search('<title>.+? — ',r).group(0).replace('<title>Объявления автора ','').replace(' — ','')
        city = response.css('div.location .an_property_value::text').get().replace('\n','')
        date = response.xpath('////div[@class="full-an-info"]//div[@class="an-history-header"]/preceding-sibling::div/text()').get().replace('\n','')
        category = response.xpath('////select[@id="sam-select2"]/option[@selected="selected"]/text()').get().replace('\n','')
        # url
        phone = response.css('span.an-contact-phone::text').get().replace('\n','').replace('-','')
        # location
        images = response.css('a.image::attr(href)').getall()

        result = {
            'external_id': id,
            'title': title,
            'description': description,
            'price': price,
            'author': author,
            'city': city,
            'date': date,
            'images': images,
            'category':  category,
            'phone': phone
        }

        yield result
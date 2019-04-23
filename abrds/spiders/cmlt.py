# scrapy runspider abrds/spiders/cmlt.py -o cmlt.json
# cd Documents/scrapy/abrds
# scrapy runspider abrds/spiders/cmlt.py

import scrapy
import datetime
import re
import requests
from scrapy.loader import ItemLoader
from scrapy.linkextractors import LinkExtractor
from abrds.items import Ad
from scrapy.contrib.spiders import Rule

class CmltSpider(scrapy.Spider):
    name = 'cmlt'
    start_urls = [
        'https://www.cmlt.ru/ads--rubric-88',        #flats
        'https://www.cmlt.ru/ads--rubric-1944'      #rooms
        # 'https://www.cmlt.ru/ad-b5167401'
    ]

    allowed_domains = [
        'cmlt.ru'
    ]

    def parse(self, response):
        # follow links to adv pages
        links = response.css('div.item a.an-bg-link::attr(href)').getall()
        links = list(set(links))
        print('LINKS TO ADS FROM PAGE:')
        print(links)
        for href in links:
            page = "https://www.cmlt.ru"+href
            print("\tPARSING PAGE"+page)
            yield response.follow(page, self.parse_item)
        # follow pagination links
        nextPage = "https://www.cmlt.ru"+response.css('a.pagesController:last-child::attr(href)').get()
        yield response.follow(nextPage, self.parse)


    def parse_item(self, response):
        print("INVOKED parse_item url")
        print(response.url)
        item = ItemLoader(item=Ad(), response=response)
        item.add_value('provider',  'cmlt')
        item.add_value('external_id',  re.search('ad-.\d+',response.url).group(0).replace('ad-', ''))
        try:
            date = response.xpath('////div[@class="full-an-info"]//div[@class="an-history-header"]/preceding-sibling::div/text()').get().replace('\n','')
        except BaseException:
            date = response.xpath('////div[@class="full-an-info"]/div[@class="fullAn"]/div[contains(@class, "view-an")]/following-sibling::div/text()').get().replace('\n','')
        date = date.replace('Сегодня', datetime.datetime.today().strftime('%Y-%m-%d'))
        date = date.replace('Вчера', (datetime.datetime.today() - datetime.timedelta(1)).strftime('%Y-%m-%d'))
        date = date.replace('\xa0',' ')
        print(date)
        try:
            date = datetime.datetime.strptime(date, "%d.%m.%Y %H:%M").strftime("%Y-%m-%d %H:%M:%S")
        except BaseException:
            None
        print(date)
        item.add_value('date', date)
        item.add_value('title', response.css('h1::text').get().replace('\n',''))
        item.add_value('description', ''.join(response.css('div.full-an-info div.view-an.content-block::text').getall()).replace('\n',''))
        try:
            item.add_value('price', response.css('tr.fullAn-price div::text').get().replace('руб.', '').replace('\n', '').replace('\xa0', '').replace(' ', ''))
        except BaseException:
            item.add_value('price', 0)
        item.add_value('address', response.css('div.location .an_property_value::text').get().replace('\n',''))

        
        coordinates = re.search('center: \[\d+.?\d+, \d+.\d+]',response.text).group(0)
        coordinates = coordinates.replace('center: [','').replace(']','')
        coordinates = coordinates.split(', ')
        item.add_value('lattitude', coordinates[0]) 
        item.add_value('longitude', coordinates[1]) 
        item.add_value('ext_category', response.xpath('////select[@id="sam-select2"]/option[@selected="selected"]/text()').get().replace('\n',''))
        images = ','.join(response.css('a.image::attr(href)').getall())
        item.add_value('images', images)
        item.add_value('videos', '') 
        item.add_value('site', '') 
        item.add_value('details', '') 
        author_url = response.css('div.an-page-other-user-ans a::attr(href)').get()
        print("URL автора: https://cmlt.ru"+author_url)
        r = requests.get('https://www.cmlt.ru'+author_url).text
        author_external_id = re.search('type="hidden" name="cid" value="\d+?"',r).group(0).replace('type="hidden" name="cid" value="','').replace('"','')
        item.add_value('author_external_id', author_external_id)
        try:
            author = re.search('<title>.+? — ',r).group(0).replace('<title>Объявления автора ','').replace(' — ','')
            author = author.replace('<title>Объявления выбранного автора', '').replace('<title>Объявления организации ', '')
        except BaseException:
            author = re.search('id="shop-name" class="userstyle_name">.+?</div>').group(0).replace('id="shop-name" class="userstyle_name">','').replace('</div>','')
        item.add_value('author', author)
        item.add_value('phone', response.css('span.an-contact-phone::text').get().replace('\n','').replace('-','')[1:])
        item.add_value('original_url', response.url[20:])
        item.add_value('created_at', 'now')
        item.add_value('processed', False)
        print('======================================================')
        print(item)

        return item.load_item()
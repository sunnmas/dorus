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
import json
import base64

class IrrSpider(scrapy.Spider):
    name = 'irr'
    start_urls = [
        'https://irr.ru/real-estate/apartments-sale/secondary/prodaetsya-1-k-kvartira-moskva-moskva-dubninskaya-advert708922038.html'
        # 'https://irr.ru/real-estate/apartments-sale/new/1-komn-kvartira-v-novostroyke-advert707860767.html'
        # 'https://irr.ru/real-estate/apartments-sale/one-rooms/moskovskaya-obl/himki-gorod/'
    ]

    allowed_domains = [
        'irr.ru'
    ]

    # def parse(self, response):
    #     # follow links to adv pages
    #     links = response.css('.listing .listing__item .listing__itemTitleWrapper a::attr(href)').getall()
    #     links = list(set(links))
    #     print('LINKS TO ADS FROM PAGE:')
    #     print(links)
    #     for href in links:
    #         page = href
    #         print("\tPARSING PAGE"+page)
    #         yield response.follow(page, self.parse_item)
    #     # follow pagination links
    #     nextPage = response.css('.pagination__pagesItem a:last-child::attr(href)').get()
    #     yield response.follow(nextPage, self.parse)


    def parse(self, response):
        print(response.url)

        item = ItemLoader(item=Ad(), response=response)

        adv = re.search("product\['listingParams'\] = {.+?}", response.text)[0]
        adv = json.loads(adv.replace("product['listingParams'] = ",''))
        item.add_value('provider',  'irr')
        id = response.css('.js-advertId::attr(value)').get()
        item.add_value('external_id', id)
        item.add_value('date', adv['date_create'])
        item.add_value('title', adv['title'])
        item.add_value('description', adv['text'])
        item.add_css('address', '.js-scrollToMap::text')
        item.add_css('address', '.productPage__metro::text')
        
        try:
            coordinates = response.css('.js-productPageMap::attr(data-map-info)').get()
            coordinates = json.loads(coordinates)
            item.add_value('lattitude', coordinates['lat']) 
            item.add_value('longitude', coordinates['lng'])
        except BaseException:
            print('coords not found')
        images = ','.join(response.css('.lineGallery img::attr(data-src)').getall())
        item.add_value('images', images)
        item.add_value('videos', '')
        site = response.css('.productPage__infoTextBold a::attr(href)').get().replace('?utm_source=irr','')
        item.add_value('site', site)
        item.add_value('details', '')

        author_external_id = re.search("var advert_user_id = '.+?';", response.text)[0]
        author_external_id = author_external_id.replace("var advert_user_id = '",'').replace("';",'')
        author_external_id = base64.b64decode(author_external_id).decode("utf-8")
        item.add_value('author_external_id', author_external_id)

        item.add_css('author', '.productPage__inlineWrapper a::text')
        item.add_css('author', '.productPage__infoTextBold.productPage__infoTextBold_inline::text')
        phone = response.css('input[name="phoneBase64"]::attr(value)').get()
        phone = base64.b64decode(phone).decode("utf-8").replace('(','').replace(')','').replace('-','').replace(' ','')[2:]
        item.add_value('phone', phone)
        url = response.url[14:]
        print(url)
        ext_category = re.search("/.*?/.*?/", url)[0][1:-1].replace('/','::')
        item.add_value('ext_category', ext_category)
        offer = re.search("::.+", ext_category)[0].replace('::','')
        item.add_value('offer', offer)
        item.add_value('original_url', url)
        item.add_value('created_at', 'now')
        item.add_value('processed', False)
        print('======================================================')
        return item.load_item()

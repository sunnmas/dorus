# cd Documents/scrapy/abrds
# scrapy runspider abrds/spiders/phtdsk.py

import scrapy
import datetime
import re
import requests
from scrapy.loader import ItemLoader
from scrapy.linkextractors import LinkExtractor
from abrds.items import Ad
from scrapy.http.cookies import CookieJar

class PhotodoskaSpider(scrapy.Spider):
    name = 'phtdsk'
    custom_settings = {
        'LOG_FILE': 'phtdsk.log',
    }
    start_urls = [
        'https://photodoska.ru/tomsk/nedvizhimost'
        # 'https://photodoska.ru/tomsk/nedvizhimost/sdam/sdayu-kvartiru-v-solnechnom-mikrorajone-3005728'
    ]

    allowed_domains = [
        'photodoska.ru'
    ]

    def parse(self, response):
        # follow links to adv pages
        links = response.css('a.img_wrapper::attr(href)').getall()
        links = list(set(links))
        print('LINKS TO ADS FROM PAGE:')
        print(links)
        for href in links:
            page = href
            print("\tPARSING PAGE"+page)
            yield response.follow(page, self.parse_item)
        # follow pagination links
        nextPage = response.css('a.pagesController:last-child::attr(href)').get()
        yield response.follow(nextPage, self.parse)


    def parse_item(self, response):
        print('----------------------------------------------------------------')
        print(response.url)
        item = ItemLoader(item=Ad(), response=response)

        cookieJar = response.meta.setdefault('cookie_jar', CookieJar())
        cookieJar.extract_cookies(response, response.request)

        item.add_value('provider',  'phtdsk')
        id = response.css('#contacts::attr(data-id)').get()
        item.add_value('external_id', id)
    #date
        date = response.css('time::text').get().replace("\r",'').replace("\t",'').replace("\n",'')
        try:
            date = datetime.datetime.strptime(date, "%H:%M %d.%m.%Y").strftime("%Y-%m-%d %H:%M:%S")
        except BaseException:
            None
        item.add_value('date', date)

        item.add_value('title', response.css('h1::text').get().replace('\n','').replace("\r",'').replace("\t",''))
        item.add_value('description', response.css('span[itemprop="description"] p::text').get())
        item.add_value('description', response.css('span[itemprop="description"] td::text').get())
    #price
        try:
            item.add_value('price', response.css('span[itemprop="price"]::text').get().replace('руб.', '').replace('\n', '').replace('\xa0', '').replace(' ', ''))
        except BaseException:
            item.add_value('price', 0)
        item.add_css('address', '.post_content h5::text')
    #coordinates
        coordinates = response.css('meta[name="geo.position"]::attr(content)').get()
        coordinates = coordinates.split(';')
        item.add_value('lattitude', coordinates[0]) 
        item.add_value('longitude', coordinates[1]) 
    #images    
        images = ','.join(response.css('.swiper-slide a::attr(href)').getall())
        item.add_value('images', images)
        item.add_value('videos', '') 
        item.add_value('site', '') 
    #author
        author_url = response.css('div.an-page-other-user-ans a::attr(href)').get()
        author_external_id = response.css('.panel-body div:nth-child(2) a::attr(href)').getall()[0].replace('/user/','')
        item.add_value('author_external_id', author_external_id)
        author = response.css('.panel-body div:nth-child(2) a::text').getall()[0]
        item.add_value('author', author)
        # item.add_value('offer', response.css('.breadcrumb a::text').getall()[1].replace('\n',''))
        item.add_value('category', response.css('.breadcrumb a::text').get().replace('\n',''))
        item.add_value('details', '') 
        
        item.add_value('original_url', response.url)
        item.add_value('created_at', 'now')
        return scrapy.FormRequest("https://photodoska.ru/?a=show_contact_rn",
                # meta = {'dont_merge_cookies': True, 'cookiejar': cookieJar},
                formdata={'id': id},
                meta={'item': item},
                callback=self.parse_phone)
        item.add_value('processed', False)
        print('======================================================')

    def parse_phone(self, response):
        print('phone answer:')
        print(response.text)
        item = response.meta['item']
        phone = re.search('"tel:\d+?"',response.text).group(0).replace('"tel:','').replace('"','')[1:]
        item.add_value('phone', phone)
        return item.load_item()
        print('******************************************************')
        # без адреса?
        # https://photodoska.ru/tomsk/nedvizhimost/prodam/prodam-dom-2991872

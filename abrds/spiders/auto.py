import scrapy
import re
import requests
from scrapy.loader import ItemLoader
from scrapy.linkextractors import LinkExtractor
from abrds.items import Ad
import json
from toripchanger import TorIpChanger

class AutoSpider(scrapy.Spider):
    name = 'auto'
    cookies = {'gdpr': '1', 'path': '/', 'max-age': '31536000', 'domain': '.auto.ru'}
    # custom_settings = {
    #     'LOG_FILE': 'auto.log',
    # }
 
    start_urls = ['https://auto.ru/cars/used/sale/volkswagen/passat/1089091058-b8c2f40b/']

    allowed_domains = [
        'auto.ru'
    ]

    def start_requests(self):
        headers = {'User-Agent': 'Mozilla/5.01 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36'}
        for i, url in enumerate(self.start_urls):
            yield scrapy.Request(url, cookies=self.cookies, callback=self.parse, headers=headers)
            # yield scrapy.Request(url, meta={'cookiejar': i}, callback=self.parse, headers=headers)

    # def parse_item(self, response):
    def parse(self, response):
        print('----------------------------------------------------------------')
        print(response.url)
        if re.search('вынуждены временно заблокировать доступ', response.text) != None:
            ip_changer = TorIpChanger(reuse_threshold=10)
            ip_changer.get_new_ip()
            raise Exception("============   ACCESS DENIED   ============")
        print(response.text)
        # print(self.cookies)
        item = ItemLoader(item=Ad(), response=response)
        url = response.url
        item.add_value('provider',  'auto')
        item.add_css('title', '.CardHead-module__title::text')



        item.add_value('original_url', url)
        item.add_value('created_at', 'now')
        item.add_value('processed', False)
        print(item)
        print('======================================================')
        csrf = response.headers.getlist('Set-Cookie')[0]
        csrf = csrf.replace('; Domain=.auto.ru; Path=/','').replace()
        sale_id = re.search('"saleId":"\d+-[abcdef0-9]+',response.text).group(0).replace('"saleId":', '')
        print('sale_id: '+sale_id)
        print('csrf: '+csrf)
        headers = {
            'content-type': 'application/x-www-form-ulencoded;charset=UTF-8',
            'x-client-app-version': '201908.30.09836',
            'x-requested-with': 'fetch'
        }
        headers['x-csrf-token'] = csrf
        print(headers)
        return scrapy.FormRequest("https://auto.ru/-/ajax/desktop/getPhones",
                formdata={'category': 'cars', 'offerIdHash': sale_id},
                meta={'item': item, 'cookiejar': response.meta['cookiejar']},
                callback=self.parse_phone,
                headers=headers
                # ,
                # cookies=self.cookies
                )

    def parse_phone(self, response):
        print('phone answer:')
        if re.search('вынуждены временно заблокировать доступ', response.text) != None:
            raise Exception("============   ACCESS DENIED   ============")
        print(response.text)
        item = response.meta['item']
        phone = 'xxxxxxxxx'
        item.add_value('phone', phone)
        return item.load_item()
        print('******************************************************')
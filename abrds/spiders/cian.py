import scrapy
import datetime
import re
import requests
from scrapy.loader import ItemLoader
from scrapy.linkextractors import LinkExtractor
from abrds.items import Ad
import json
import base64

class CianSpider(scrapy.Spider):
    name = 'cian'
    custom_settings = {
        'LOG_FILE': 'cian.log',
    }
    start_urls = [
        'https://saransk.cian.ru/sale/flat/198831288/'
        # Продажа квартир
        # 'https://kazan.cian.ru/kupit-kvartiru/',
        # 'https://ekb.cian.ru/kupit-kvartiru/',
        # 'https://omsk.cian.ru/kupit-kvartiru/',
        # 'https://spb.cian.ru/kupit-kvartiru/',
        # 'https://sevastopol.cian.ru/kupit-kvartiru/',
        # 'https://sochi.cian.ru/kupit-kvartiru/',
        # 'https://kostroma.cian.ru/kupit-kvartiru/',

        # 'https://kazan.cian.ru/kupit-kvartiru-novostroyki/',
        # 'https://ekb.cian.ru/kupit-kvartiru-novostroyki/',
        # 'https://omsk.cian.ru/kupit-kvartiru-novostroyki/',
        # 'https://spb.cian.ru/kupit-kvartiru-novostroyki/',
        # 'https://sevastopol.cian.ru/kupit-kvartiru-novostroyki/',
        # 'https://sochi.cian.ru/kupit-kvartiru-novostroyki/',
        # 'https://kostroma.cian.ru/kupit-kvartiru-novostroyki/',
    ]

    allowed_domains = [
        'cian.ru'
    ]

    def parse_details(self, details, category, title, url):
        arr = [u'Этаж', u'Всего комнат', u'Комнат в квартире', u'Площадь кухни',
            u'Год постройки', u'Общая площадь', u'Жилая площадь', u'Высота потолков', u'До метро',
           u'Лифты в здании', u'Материал стен', u'Санузел', u'Приватизированная квартира', 
           u'Площадь арендуемой комнаты', u'Можно с животными', u'Комиссия', u'Период аренды',
           u'Комнат сдается', u'Доля', u'Тип здания',
           u'Площадь участка', u'Категория земли', u'Вид разрешенного использования',
           u'Отапливаемый', u'Мебель', u'Бытовая техника', u'Интернет',
           u'Количество этажей', u'Количество комнат', u'Количество спален',
           u'Гараж', u'Охрана']
        subs = [
                [u' м,', u','], [u' г.', u''],
                [u' мин/пеш', u''], [u' км', u''],
                [u'Этажей в здании', u'Этажей'],
                [u'Комнат в квартире', u'Количество комнат'],
                [u'Год постройки', u'Год постройки'],
                [u'До метро, минут(пешком)', u'До метро пешком'],
                [u'Материал стен', u'Тип здания'],
                [u'Приватизированная квартира', u'Приватизированная квартира": "1'],
                [u'Можно с животными', u'Можно с животными": "1'],
                [u'Лифты в здании', u'Лифт": "1'],
                [u'Отапливаемый', u'Отапливаемый": "1'],
                [u'Мебель', u'Мебель": "1'],
                [u'Бытовая техника', u'Бытовая техника": "1'],
                [u'Интернет', u'Интернет": "1'],
                [u'Гараж', u'Гараж": "1'],
                [u'Охрана', u'Охрана": "1']
            ]
        result = []
        print('draft details: '+'='.join(details))
        for i in details:
            for j in arr:
                if not (re.search(j, i) is None):
                    result.append('"'+i.strip().replace(': ','": "')+'"')
        offer = re.search("::.+", category).group(0).replace('::','')
        offer = offer.replace('apartments-sale', 'Продам')
        offer = offer.replace('rooms-sale', 'Продам')
        offer = offer.replace('rooms-rent', 'Сдам')
        offer = offer.replace('commercial-sale', 'Продам')
        offer = offer.replace('commercial', 'Сдам в аренду')
        offer = offer.replace('out-of-town-rent', 'Сдам')
        offer = offer.replace('out-of-town', 'Продам')
        offer = offer.replace('rent', 'Сдам')
        result.append('"Тип предложения": "'+offer+'"')
        if (category == 'real-estate::apartments-sale') or (category == "real-estate::rent"):
            if re.search('Студия, ', title) != None:
                result.append('"Студия": "1"')
            else:
                result.append('"Студия": "0"')

            if re.search('/secondary/', url) != None:
                result.append('"Вторичное жилье": "1"')
            else:
                result.append('"Вторичное жилье": "0"')

        result = '{'+', '.join(result)+'}'
        result = result.replace(' м"', '"')
        result = result.replace(' сот"', '"')

        for k in subs:
            result = result.replace(k[0], k[1])
        print("details: "+result)
        return result

    def parse2(self, response):
        # Определяем список ссылок со страницы
        links = response.css('a[class*="--header--"]::attr(href)').getall()
        links = list(set(links))
        print('LINKS TO ADS FROM PAGE:')
        print(links)
        for href in links:
            page = href
            print("\tPARSING PAGE"+page)
            yield response.follow(page, self.parse_item)
        # ссылки на следующие страницы
        
        try:
            nextPage = response.xpath('////li[contains(@class,"--list-item--active--")]/following-sibling::li/a/@href').get()
            yield response.follow(nextPage, self.parse)
        except BaseException:
            print('bye')
        
    def parse(self, response):
        print('----------------------------------------------------------------')
        print(response.url)
        item = ItemLoader(item=Ad(), response=response)

        item.add_value('provider',  'cian')
        id = re.search("объявление №\d+", response.css('title::text').get()).group(0).replace('объявление №','')
        item.add_value('external_id', id)

        item.add_css('date', 'div[class*="--container--"]::text')
        item.add_css('title', 'h1::text')
        description = "\x0d".join(response.css('p[class*="--description-text--"]::text').getall())
        item.add_value('description', description)
        item.add_css('price', 'span[class*="--price_value--"] span::text')
        address = ', '.join(response.css('address[class*="--address--"] a::text').getall())
        item.add_value('address', address)
        
        try:
            coordinates = re.search("center=\d+.\d+,\d+.\d+", response.text).group(0).replace('center=','')
            coordinates = coordinates.split(',')
            item.add_value('lattitude', coordinates[0])
            item.add_value('longitude', coordinates[1])
        except BaseException:
            try:
                coordinates = re.search("center=\d+.\d+%2C\d+.\d+", response.text).group(0).replace('center=','')
                coordinates = coordinates.split('%2C')
                item.add_value('lattitude', coordinates[0])
                item.add_value('longitude', coordinates[1])
            except BaseException:
                print('coords not found')
                item.add_value('lattitude', '0')
                item.add_value('longitude', '0')
        re.findall('"fullUrl":"https:.+?"',response.text)
        images = ','.join(re.findall('"fullUrl":"https:.+?.jpg',response.text)).replace('"fullUrl":"','').replace('\\u002F','/')
        item.add_value('images', images)
        item.add_value('videos', '')
        item.add_value('site', '')
        author_external_id = re.search('"ownerCianId":\d+',response.text).group(0).replace('"ownerCianId":', '')
        item.add_value('author_external_id', author_external_id)
        author = response.css('h2[class*="--title--"]::text').get()
        if re.search(author_external_id, author) != None:
            item.add_value('author', 'Нет имени')
        else:
            item.add_css('author', 'h2[class*="--title--"]::text')

        phone = re.search('\+7\d+',response.text).group(0)
        item.add_value('phone', phone)
        url = response.url
        draft_category = re.search("cian.ru/.*?/.*?/", url).group(0)[0:-1].replace('cian.ru/','').replace('/','::')
        category = draft_category.replace('sale::flat', 'Квартиры, комнаты')
        item.add_value('category', category)
        item.add_value('details', '')
#         details = response.css('.productPage__infoColumnBlockText::text').getall()
#         details = self.parse_details(details, draft_category, title, response.url)
#         item.add_value('details', details)

#         category = category.replace('real-estate::rooms-sale', 'Квартиры, комнаты')
#         category = category.replace('real-estate::rooms-rent', 'Квартиры, комнаты')
#         category = category.replace('real-estate::rent', 'Квартиры, комнаты')
#         category = category.replace('real-estate::commercial-sale', 'Коммерческая недвижимость')
#         category = category.replace('real-estate::commercial', 'Коммерческая недвижимость')
#         if category == 'real-estate::out-of-town-rent':
#             if "real-estate/out-of-town-rent/lands" in url:
#                 category = category.replace('real-estate::out-of-town-rent', 'Земельные участки')
#             else:
#                 category = category.replace('real-estate::out-of-town-rent', 'Дома, дачи, коттеджи')
#         if category == 'real-estate::out-of-town':
#             if "real-estate/out-of-town/lands" in url:
#                 category = category.replace('real-estate::out-of-town', 'Земельные участки')
#             else:
#                 category = category.replace('real-estate::out-of-town', 'Дома, дачи, коттеджи')
#         category = category.replace('real-estate::out-of-town', 'Дома, дачи, коттеджи')

        item.add_value('original_url', url)
        item.add_value('created_at', 'now')
        item.add_value('processed', False)
        print('======================================================')
        return item.load_item()
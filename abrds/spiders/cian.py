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
    start_preurls = [
        # 'https://check.torproject.org/'
        # 'https://saransk.cian.ru/sale/flat/198831288/'
        # Продажа квартир
        'cian.ru/kupit-kvartiru/',
        'cian.ru/kupit-kvartiru-novostroyki/',
        'cian.ru/kupit-dom/'
    ]

    start_urls = []

    subdomains = ['spb',
                'novosibirsk',
                'ekb',
                'nn',
                'kazan',
                'chelyabinsk',
                'omsk',
                'samara',
                'rostov',
                'ufa',
                'krasnoyarsk',
                'perm',
                'voronezh',
                'volgograd',
                'krasnodar',
                'saratov',
                'tyumen',
                'tolyatti',
                'izhevsk',
                'barnaul',
                'ulyanovsk',
                'irkutsk',
                'habarovsk',
                'yaroslavl',
                'vladivostok',
                'mahachkala'
                'tomsk',
                'orenburg',
                'kemerovo',
                'ryazan',
                'astrahan',
                'naberezhnye-chelny',
                'penza',
                'lipetsk',
                'kirov',
                'cheboksary',
                'tula',
                'kaliningrad',
                'balashikha',
                'kursk',
                'sevastopol',
                'ulan-ude',
                'stavropol',
                'sochi',
                'tver',
                'ivanovo',
                'bryansk',
                'belgorod',
                'surgut',
                'vladimir',
                'arhangelsk',
                'chita',
                'krym',
                'kaluga',
                'smolensk',
                'saransk',
                'kurgan',
                'cherepovec',
                'orel',
                'vologda',
                'yakutsk',
                'vladikavkaz',
                'podolsk',
                'groznyy',
                'murmansk',
                'tambov',
                'petrozavodsk',
                'kostroma',
                'hmao',
                'novorossiysk',
                'yoshkar-ola',
                'khimki',
                'rostov'
                ]

    for subdomain in subdomains:
        for base_url in start_preurls:
            start_urls.append('https://'+subdomain+'.'+base_url)


    allowed_domains = [
        'cian.ru'
    ]

    def parse_details(self, response, offer):
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
                [u'Общая', u'Общая площадь'],
                [u'Жилая', u'Жилая площадь'],
                [u'Построен', u'Год постройки'],
                [u'Кухня', u'Площадь кухни']
            ]
        result = []
        general_details_titles = response.css('div[class*="--info-title--"]::text').getall()
        general_details_values = response.css('div[class*="--info-text--"]::text').getall()
        additional_details_titles = response.css('div[class*="--item--"] div[class*="--name--"]::text').getall()
        additional_details_values = response.css('div[class*="--item--"] div[class*="--value--"]::text').getall()

        for id, val in enumerate(general_details_titles):
            if val == 'Этаж':
                fl = re.search("\d", general_details_values[id]).group(0)
                fls = re.search("из \d", general_details_values[id]).group(0).replace('из ', '')
                result.append('"Этаж": "'+fl+'"')
                result.append('"Этажей": "'+fls+'"')
            else:
                result.append('"'+val+'": "'+general_details_values[id].replace(',', '.')+'"')

        for id, val in enumerate(additional_details_titles):
            result.append('"'+val+'": "'+additional_details_values[id].replace(',', '.')+'"')

        if offer == 'newBuildingFlatSale':
            result.append('"Новостройка": "1"')
        offer = offer.replace('flatSale', 'Продам')
        offer = offer.replace('landSale', 'Продам')
        offer = offer.replace('houseSale', 'Продам')
        offer = offer.replace('houseShareSale', 'Продам')
        offer = offer.replace('cottageSale', 'Продам')
        offer = offer.replace('roomSale', 'Продам')
        offer = offer.replace('newBuildingFlatSale', 'Продам')
        
        offer = offer.replace('flatRent', 'Сдам')
        offer = offer.replace('landRent', 'Сдам')
        offer = offer.replace('houseRent', 'Сдам')
        offer = offer.replace('houseShareRent', 'Сдам')
        offer = offer.replace('cottageRent', 'Сдам')
        offer = offer.replace('roomRent', 'Сдам')

        result.append('"Тип предложения": "'+offer+'"')

        result = '{'+', '.join(result)+'}'
        result = result.replace(' м²"', '"')
        result = result.replace(' сот."', '"')

        for k in subs:
            result = result.replace(k[0], k[1])
        print("details: "+result)
        return result

    def parse(self, response):
        # Определяем список ссылок со страницы
        links = response.css('a[class*="--header--"]::attr(href)').getall()
        links = list(set(links))
        print('LINKS TO ADS FROM PAGE ('+response.url+'):')
        print(links)
        for href in links:
            page = href
            print("\tPARSING PAGE: "+page)
            yield response.follow(page, self.parse_item)

        # ссылки на следующие страницы
        try:
            nextPage = response.xpath('////li[contains(@class,"--list-item--active--")]/following-sibling::li/a/@href').get()
            yield response.follow(nextPage, self.parse)
        except BaseException:
            print('bye')
        
    def parse_item(self, response):
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
        images = ','.join(re.findall('"fullUrl":"https:\\\\[\w\\\\.\d-]+.jpg',response.text)).replace('"fullUrl":"','').replace('\\u002F','/')
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
        draft_category = re.search('"category":".+?"', response.text).group(0).replace('"category":"','').replace('"','')
        # re.search("cian.ru/.*?/.*?/", url).group(0)[0:-1].replace('cian.ru/','').replace('/','::')
        category = draft_category.replace('flatSale', 'Квартиры, комнаты')
        category = category.replace('flatRent', 'Квартиры, комнаты')
        category = category.replace('roomSale', 'Квартиры, комнаты')
        category = category.replace('roomRent', 'Квартиры, комнаты')
        category = category.replace('newBuildingFlatSale', 'Квартиры, комнаты')
        category = category.replace('landSale', 'Земельные участки')
        category = category.replace('landRent', 'Земельные участки')
        category = category.replace('houseShareSale', 'Дома, дачи, коттеджи')
        category = category.replace('houseSale', 'Дома, дачи, коттеджи')
        category = category.replace('houseRent', 'Дома, дачи, коттеджи')
        category = category.replace('cottageRent', 'Дома, дачи, коттеджи')
        category = category.replace('cottageSale', 'Дома, дачи, коттеджи')
        item.add_value('category', category)


        details = self.parse_details(response, draft_category)
        item.add_value('details', details)

#         details = response.css('.productPage__infoColumnBlockText::text').getall()

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
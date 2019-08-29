import scrapy
import datetime
import re
import requests
from scrapy.loader import ItemLoader
from scrapy.linkextractors import LinkExtractor
from abrds.items import Ad
import json
import base64

from scrapy.spiders import SitemapSpider

# class CianSpider(SitemapSpider):
class CianSpider(scrapy.Spider):

    name = 'cian'
    allowed_domains = [
        'cian.ru'
    ]
    # custom_settings = {
    #     'LOG_FILE': 'cian1.log',
    # }
    start_preurls = [
        'kupit-kvartiru-novostroyki',

        'kupit-kvartiru',
        'snyat-kvartiru',
        
        'kupit-komnatu',
        'snyat-komnatu',

        'kupit-dom',
        'snyat-dom',

        'kupit-sklad',
        'snyat-sklad',
        
        'kupit-ofis',
        'snyat-ofis',

        'kupit-torgovuyu-ploshad',
        'snyat-torgovuyu-ploshad',

        'kupit-pomeshenie-svobodnogo-naznachenija',
        'snyat-pomeshenie-svobodnogo-naznachenija',

        'kupit-garazh',
        'snyat-garazh'
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
                'khimki'
                ]

    for subdomain in subdomains:
        for base_url in start_preurls:
            start_urls.append('https://'+subdomain+'.cian.ru/'+base_url+'/')

    # sitemap_urls = ['https://www.cian.ru/sitemap.xml']
    # sitemap_follow = True

    # start_urls = ['https://kaluga.cian.ru/sale/flat/215250718/']
        

    def parse(self, response):
    # def parse_dummy(self, response):
        # Определяем список ссылок со страницы
        links = response.css('a[class*="--header--"]::attr(href)').getall()
        links = list(set(links))
        print('LINKS TO ADS FROM PAGE ('+response.url+'):')
        print(links)
        for href in links:
            page = href
            print("\tPARSING ITEM: "+page)
            yield response.follow(page, self.parse_item)

        # ссылки на следующие страницы
        try:
            nextPage = response.xpath('////li[contains(@class,"--list-item--active--")]/following-sibling::li/a/@href').get()
            yield response.follow(nextPage, self.parse)
        except BaseException:
            print('bye')
  
    def parse_item(self, response):
    # def parse(self, response):
        print('----------------------------------------------------------------')
        print(response.url)
        item = ItemLoader(item=Ad(), response=response)

        item.add_value('provider',  'cian')
        actual = response.css('div[class*="--offer_card_page-top--"]>div[class*="--container--"]::text').get()
        if actual == 'Объявление снято с публикации':
            item.add_value('actual', False)
        else:
            item.add_value('actual', True)

        id = re.search("/\d+/", response.url).group(0).replace('/','')
        item.add_value('external_id', id)


        date = response.css('div[class*="--container--"]::text').get()
        try:
            date = date.replace('янв,', 'Jan').replace('фев,', 'Feb').replace('мар,', 'Mar')
            date = date.replace('апр,', 'Apr').replace('мая,', 'May').replace('июня,', 'Jun')
            date = date.replace('июля,', 'Jul').replace('авг,', 'Aug').replace('сент,', 'Sep')
            date = date.replace('окт,', 'Oct').replace('нояб,', 'Nov').replace('дек,', 'Dec')
            date = str(datetime.datetime.now().year)+'-'+datetime.datetime.strptime(date, '%d %b %H:%M').strftime('%m-%d')
            item.add_value('date', date)
        except BaseException:
            item.add_css('date', 'div[class*="--container--"]::text')
        item.add_css('title', 'h1::text')
        description = "\x0d".join(response.css('p[class*="--description-text--"]::text').getall())
        item.add_value('description', description)
        item.add_css('price', 'span[class*="--price_value--"] span::text')
        item.add_css('price_unit', 'span[class*="--price_value--"] span::text')
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

        images = ','.join(re.findall('"fullUrl":"https:\\\\[\w\\\\.\d-]+.jpg',response.text)[:10]).replace('"fullUrl":"','').replace('\\u002F','/')
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
        
        if response.css('span[class*="--tag-pro--"]::text').get() == 'Pro':
            item.add_value('company', True)
        else:
            item.add_value('company', False)

        phone = re.search('\+7\d+',response.text).group(0)
        item.add_value('phone', phone)
        url = response.url
        draft_category = re.search('"category":".+?"', response.text).group(0).replace('"category":"','').replace('"','')

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
        category = category.replace('warehouseSale', 'Коммерческая недвижимость')
        category = category.replace('warehouseRent', 'Коммерческая недвижимость')
        category = category.replace('officeSale', 'Коммерческая недвижимость')
        category = category.replace('officeRent', 'Коммерческая недвижимость')
        category = category.replace('shoppingAreaSale', 'Коммерческая недвижимость')
        category = category.replace('shoppingAreaRent', 'Коммерческая недвижимость')
        category = category.replace('freeAppointmentObjectSale', 'Коммерческая недвижимость')
        category = category.replace('freeAppointmentObjectRent', 'Коммерческая недвижимость')
        category = category.replace('garageSale', 'Гаражи и машиноместа')
        category = category.replace('garageRent', 'Гаражи и машиноместа')
        item.add_value('category', category)

        details = self.parse_details(response, draft_category)
        item.add_value('details', details)
        item.add_value('original_url', url)
        item.add_value('created_at', 'now')
        item.add_value('processed', False)
        print('======================================================')
        return item.load_item()

    def parse_details(self, response, offer):
        subs = [
                [u' м,', u','], [u' г.', u''],
                [u' мин/пеш', u''], [u' км', u''],
                [u'Общая', u'Общая площадь'],
                [u'Жилая', u'Жилая площадь'],
                [u'Построен', u'Год постройки'],
                [u'Кухня', u'Площадь кухни'],
                [u'Участок', u'Площадь участка'],
                [u'Тип дома', u'Тип здания'],
                [u'Этажей в доме', u'Этажей'],
                [u'Этажей в доме', u'Этажей'],
            ]
        result = []
        general_details_titles = response.css('div[class*="--info-title--"]::text').getall()
        general_details_values = response.css('div[class*="--info-text--"]::text').getall()
        additional_details_titles = response.css('div[class*="--item--"] div[class*="--name--"]::text').getall()
        additional_details_values = response.css('div[class*="--item--"] div[class*="--value--"]::text').getall()

        for id, val in enumerate(general_details_titles):
            if val == 'Этаж':
                fl = re.search("\d+", general_details_values[id]).group(0)
                fls = re.search("из \d+", general_details_values[id]).group(0).replace('из ', '')
                result.append('"Этаж": "'+fl+'"')
                result.append('"Этажей": "'+fls+'"')
            else:
                result.append('"'+val+'": "'+general_details_values[id].replace(',', '.')+'"')

        for id, val in enumerate(additional_details_titles):
            result.append('"'+val+'": "'+additional_details_values[id].replace(',', '.')+'"')

        if offer == 'newBuildingFlatSale':
            result.append('"Тип жилья": "Новостройка"')
        else:
            result.append('"Тип жилья": "Вторичное жилье"')
        if offer == 'warehouseSale' or offer == 'warehouseRent':
            result.append('"Тип объекта": "Складское помещение"')
        if offer == 'officeRent' or offer == 'officeRent':
            result.append('"Тип объекта": "Офисное помещение"')
        if offer == 'shoppingAreaRent' or offer == 'shoppingAreaSale':
            result.append('"Тип объекта": "Торговое помещение"')
        if offer == 'freeAppointmentObjectRent' or offer == 'freeAppointmentObjectSale':
            result.append('"Тип объекта": "Помещение свободного назначения"')
        offer = offer.replace('flatSale', 'Продам')
        offer = offer.replace('landSale', 'Продам')
        offer = offer.replace('houseSale', 'Продам')
        offer = offer.replace('houseShareSale', 'Продам')
        offer = offer.replace('cottageSale', 'Продам')
        offer = offer.replace('roomSale', 'Продам')
        offer = offer.replace('newBuildingFlatSale', 'Продам')
        offer = offer.replace('warehouseSale', 'Продам')
        offer = offer.replace('shoppingAreaSale', 'Продам')
        offer = offer.replace('garageSale', 'Продам')
        offer = offer.replace('freeAppointmentObjectSale', 'Продам')
        
        offer = offer.replace('flatRent', 'Сдам')
        offer = offer.replace('landRent', 'Сдам')
        offer = offer.replace('houseRent', 'Сдам')
        offer = offer.replace('houseShareRent', 'Сдам')
        offer = offer.replace('cottageRent', 'Сдам')
        offer = offer.replace('roomRent', 'Сдам')
        offer = offer.replace('warehouseRent', 'Сдам')
        offer = offer.replace('shoppingAreaRent', 'Сдам')
        offer = offer.replace('garageRent', 'Сдам')
        offer = offer.replace('freeAppointmentObjectRent', 'Сдам')

        result.append('"Тип предложения": "'+offer+'"')

        title = response.css('h1::text').get()
        if re.match('1-комн. ', title) != None:
            result.append('"Количество комнат": "1"')
        elif re.match('2-комн. ', title) != None:
            result.append('"Количество комнат": "2"')
        elif re.match('3-комн. ', title) != None:
            result.append('"Количество комнат": "3"')

        result = '{'+', '.join(result)+'}'
        result = result.replace(' м²"', '"')
        result = result.replace(' сот."', '"')

        for k in subs:
            result = result.replace(k[0], k[1])
        print("details: "+result)
        return result
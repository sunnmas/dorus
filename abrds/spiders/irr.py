# cd Documents/scrapy/abrds
# scrapy runspider abrds/spiders/irr.py
# shub deploy 392088
# C:\Users\A\Anaconda3\Scripts>activate.bat base && python --version && conda.bat deactivate


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
    # custom_settings = {
    #     'LOG_FILE': 'irr.log',
    # }
    start_urls = [
        # Продажа квартир и студий
        'https://irr.ru/real-estate/apartments-sale/moskovskaya-obl/'
        'https://saint-petersburg.irr.ru/real-estate/apartments-sale/', 
        'https://irr.ru/real-estate/apartments-sale/',
        'https://kazan.irr.ru/real-estate/apartments-sale/',
        'https://tolyatti.irr.ru/real-estate/apartments-sale/',
        'https://ekaterinburg.irr.ru/real-estate/apartments-sale/',
        'https://krasnodar.irr.ru/real-estate/apartments-sale/',
        'https://perm.irr.ru/real-estate/apartments-sale/',

        #Аренда квартир и студий
        'https://irr.ru/real-estate/rent/moskovskaya-obl/',
        'https://saint-petersburg.irr.ru/real-estate/rent/', 
        'https://irr.ru/real-estate/rent/',
        'https://kazan.irr.ru/real-estate/rent/',
        'https://tolyatti.irr.ru/real-estate/rent/',
        'https://ekaterinburg.irr.ru/real-estate/rent/',
        'https://krasnodar.irr.ru/real-estate/rent/',
        'https://perm.irr.ru/real-estate/rent/',

        # Продажа комнат
        'https://irr.ru/real-estate/rooms-sale/moskovskaya-obl/'
        'https://saint-petersburg.irr.ru/real-estate/rooms-sale/', 
        'https://irr.ru/real-estate/rooms-sale/',
        'https://kazan.irr.ru/real-estate/rooms-sale/',
        'https://tolyatti.irr.ru/real-estate/rooms-sale/',
        'https://ekaterinburg.irr.ru/real-estate/rooms-sale/',
        'https://krasnodar.irr.ru/real-estate/rooms-sale/',
        'https://perm.irr.ru/real-estate/rooms-sale/',

        # Аренда комнат
        'https://irr.ru/real-estate/rooms-rent/moskovskaya-obl/'
        'https://saint-petersburg.irr.ru/real-estate/rooms-rent/', 
        'https://irr.ru/real-estate/rooms-rent/',
        'https://kazan.irr.ru/real-estate/rooms-rent/',
        'https://tolyatti.irr.ru/real-estate/rooms-rent/',
        'https://ekaterinburg.irr.ru/real-estate/rooms-rent/',
        'https://krasnodar.irr.ru/real-estate/rooms-rent/',
        'https://perm.irr.ru/real-estate/rooms-rent/',

        #Продажа коммерческой недвижимости
        'https://irr.ru/real-estate/commercial-sale/moskovskaya-obl/',
        'https://saint-petersburg.irr.ru/real-estate/commercial-sale/', 
        'https://irr.ru/real-estate/commercial-sale/',
        'https://kazan.irr.ru/real-estate/commercial-sale/',
        'https://tolyatti.irr.ru/real-estate/commercial-sale/',
        'https://ekaterinburg.irr.ru/real-estate/commercial-sale/',
        'https://krasnodar.irr.ru/real-estate/commercial-sale/',
        'https://perm.irr.ru/real-estate/commercial-sale/',

        #Аренда коммерческой недвижимости
        'https://irr.ru/real-estate/commercial/moskovskaya-obl/',
        'https://saint-petersburg.irr.ru/real-estate/commercial/', 
        'https://irr.ru/real-estate/commercial/',
        'https://kazan.irr.ru/real-estate/commercial/',
        'https://tolyatti.irr.ru/real-estate/commercial/',
        'https://ekaterinburg.irr.ru/real-estate/commercial/',
        'https://krasnodar.irr.ru/real-estate/commercial/',
        'https://perm.irr.ru/real-estate/commercial/',

        #Дома, коттеджи, участки продажа
        'https://irr.ru/real-estate/out-of-town/moskovskaya-obl/',
        'https://saint-petersburg.irr.ru/real-estate/out-of-town/', 
        'https://irr.ru/real-estate/out-of-town/',
        'https://kazan.irr.ru/real-estate/out-of-town/',
        'https://tolyatti.irr.ru/real-estate/out-of-town/',
        'https://ekaterinburg.irr.ru/real-estate/out-of-town/',
        'https://krasnodar.irr.ru/real-estate/out-of-town/',
        'https://perm.irr.ru/real-estate/out-of-town/',

        #Дома, коттеджи, участки аренда
        'https://irr.ru/real-estate/out-of-town-rent/moskovskaya-obl/',
        'https://saint-petersburg.irr.ru/real-estate/out-of-town-rent/', 
        'https://irr.ru/real-estate/out-of-town-rent/',
        'https://kazan.irr.ru/real-estate/out-of-town-rent/',
        'https://tolyatti.irr.ru/real-estate/out-of-town-rent/',
        'https://ekaterinburg.irr.ru/real-estate/out-of-town-rent/',
        'https://krasnodar.irr.ru/real-estate/out-of-town-rent/',
        'https://perm.irr.ru/real-estate/out-of-town-rent/'

    ]
    # start_urls = ['https://irr.ru/real-estate/apartments-sale/secondary/prodaetsya-trehkomnatnaya-kvartira-na-vtorom-etazhe-advert711341141.html']

    allowed_domains = [
        'irr.ru'
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

    def parse(self, response):
        # Определяем список ссылок со страницы
        links = response.css('.listing .listing__item .listing__itemTitleWrapper a::attr(href)').getall()
        links = list(set(links))
        print('LINKS TO ADS FROM PAGE:')
        print(links)
        for href in links:
            page = href
            print("\tPARSING PAGE"+page)
            yield response.follow(page, self.parse_item)
        # ссылки на следующие страницы
        try:
            cur_page_id = int(re.search('/page\d+', response.url).group(0).replace('/page',''))
            nextPage = response.url.replace('page'+str(cur_page_id),'')+'page'+str(cur_page_id + 1)
        except BaseException:
            next_page_id = 2
            nextPage = response.url+'page2'
        yield response.follow(nextPage, self.parse)


    def parse_item(self, response):
        print('----------------------------------------------------------------')
        print(response.url)
        item = ItemLoader(item=Ad(), response=response)

        adv = re.search("product\['listingParams'\] = {.+?}", response.text).group(0)
        adv = json.loads(adv.replace("product['listingParams'] = ",''))
        item.add_value('provider',  'irr')
        id = response.css('.js-advertId::attr(value)').get()
        item.add_value('external_id', id)
        item.add_value('date', adv['date_create'])
        title = response.css('.productPage__title::text').get()
        item.add_value('title', title)
        item.add_value('description', adv['text'])
        item.add_css('price', '.productPage__price::attr(content)')
        item.add_css('address', '.js-scrollToMap::text')
        item.add_css('address', '.productPage__metro::text')
        
        try:
            coordinates = response.css('.js-productPageMap::attr(data-map-info)').get()
            coordinates = json.loads(coordinates)
            item.add_value('lattitude', coordinates['lat'])
            item.add_value('longitude', coordinates['lng'])
        except BaseException:
            print('coords not found')
            item.add_value('lattitude', '0')
            item.add_value('longitude', '0')
        images = ','.join(response.css('.lineGallery img::attr(data-src)').getall())
        item.add_value('images', images)
        item.add_value('videos', '')
        try:
            site = response.css('.productPage__infoTextBold a::attr(href)').get().replace('?utm_source=irr','')
            if 'irr.ru' in site:
                site = ''
        except BaseException:
            site = ''
        item.add_value('site', site)

        author_external_id = re.search("var advert_user_id = '.+?';", response.text).group(0)
        author_external_id = author_external_id.replace("var advert_user_id = '",'').replace("';",'')
        author_external_id = base64.b64decode(author_external_id).decode("utf-8")
        item.add_value('author_external_id', author_external_id)

        item.add_css('author', '.productPage__inlineWrapper a::text')
        item.add_css('author', '.productPage__infoTextBold.productPage__infoTextBold_inline::text')
        phone = response.css('input[name="phoneBase64"]::attr(value)').get()
        phone = base64.b64decode(phone).decode("utf-8").replace('(','').replace(')','').replace('-','').replace(' ','')[2:]
        item.add_value('phone', phone)
        url = response.url
        draft_category = re.search("irr.ru/.*?/.*?/", url).group(0)[0:-1].replace('irr.ru/','').replace('/','::')
        details = response.css('.productPage__infoColumnBlockText::text').getall()
        details = self.parse_details(details, draft_category, title, response.url)
        item.add_value('details', details)

        category = draft_category.replace('real-estate::apartments-sale', 'Квартиры, комнаты')
        category = category.replace('real-estate::rooms-sale', 'Квартиры, комнаты')
        category = category.replace('real-estate::rooms-rent', 'Квартиры, комнаты')
        category = category.replace('real-estate::rent', 'Квартиры, комнаты')
        category = category.replace('real-estate::commercial-sale', 'Коммерческая недвижимость')
        category = category.replace('real-estate::commercial', 'Коммерческая недвижимость')
        if category == 'real-estate::out-of-town-rent':
            if "real-estate/out-of-town-rent/lands" in url:
                category = category.replace('real-estate::out-of-town-rent', 'Земельные участки')
            else:
                category = category.replace('real-estate::out-of-town-rent', 'Дома, дачи, коттеджи')
        if category == 'real-estate::out-of-town':
            if "real-estate/out-of-town/lands" in url:
                category = category.replace('real-estate::out-of-town', 'Земельные участки')
            else:
                category = category.replace('real-estate::out-of-town', 'Дома, дачи, коттеджи')
        category = category.replace('real-estate::out-of-town', 'Дома, дачи, коттеджи')
        item.add_value('category', category)

        item.add_value('original_url', url)
        item.add_value('created_at', 'now')
        item.add_value('processed', False)
        print('======================================================')
        return item.load_item()
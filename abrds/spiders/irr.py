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
    start_preurls = [
        # 'real-estate/apartments-sale',     # Продажа квартир и студий
        # 'real-estate/rent',                # Аренда квартир и студий
        # 'real-estate/rooms-sale',          # Продажа комнат
        # 'real-estate/rooms-rent',          # Аренда комнат
        # 'real-estate/commercial-sale',     # Продажа коммерческой недвижимости
        # 'real-estate/commercial',          # Аренда коммерческой недвижимости
        # 'real-estate/out-of-town',         # Дома, коттеджи, участки продажа
        # 'real-estate/out-of-town-rent',    # Дома, коттеджи, участки аренда
        'real-estate/garage/',             # Продажа гаражей и машиномест
        'real-estate/garage-rent/'         # Аренда гаражей и машиномест   
    ]


    subdomains = [
        'saint-petersburg',
        'novosibirsk',
        'ekaterinburg',
        'nizhniynovgorod',
        'kazan',
        'chelyabinsk',
        'omsk',
        'samara',
        'rostovnadonu',
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
        'yaroslavl',
        'vladivostok',
        'mahachkala'
        'tomsk',
        'orenburg',
        'kemerovo',
        'ryazan',
        'astrahan',
        'nabchelny',
        'penza',
        'lipetsk',
        'kirov',
        'cheboksary',
        'tula',
        'kaliningrad',
        'kursk',
        'sevastopol',
        'ulanude',
        'stavropol',
        'sochi',
        'tver',
        'ivanovo',
        'bryansk',
        'belgorod',
        'surgut',
        'vladimir',
        'arhangelsk',
        'kaluga',
        'smolensk',
        'saransk',
        'kurgan',
        'orel',
        'vologda',
        'yakutsk',
        'vladikavkaz',
        'groznyi',
        'murmansk',
        'tambov',
        'petrozavodsk',
        'kostroma',
        'novorossiysk',
        'yoshkarola'
    ]
    start_urls = []
    for subdomain in subdomains:
        for base_url in start_preurls:
            start_urls.append('https://'+subdomain+'.irr.ru/'+base_url+'/')
    for base_url in start_preurls:
        start_urls.append('https://.irr.ru/'+base_url+'moskovskaya-obl/')
        start_urls.append('https://saint-petersburg.irr.ru/'+base_url+'leningradskaya-obl/')

    # start_urls = ['https://perm.irr.ru/real-estate/commercial-sale/offices/ofis-152-6-kv-m-zhiloy-dom-otdel-nyy-vhod-semchenko-advert520921405.html']

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
        offer = offer.replace('garage-rent', 'Сдам')
        offer = offer.replace('garage', 'Продам')
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

    # def parse_dummy(self, response):
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
    # def parse(self, response):
        print('----------------------------------------------------------------')
        print(response.url)
        item = ItemLoader(item=Ad(), response=response)

        actual = response.css('div[class="productPage__unactiveBlockTitle"]::text').get()
        if actual == 'Объявление снято с публикации':
            actual = False
            item.add_value('actual', False)
        else:
            actual = True
            item.add_value('actual', True)
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
        images = ','.join(response.css('.lineGallery img::attr(data-src)').getall()[:10])
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

        if actual == True:
            item.add_css('author', '.productPage__inlineWrapper a::text')
            item.add_css('author', '.productPage__infoTextBold.productPage__infoTextBold_inline::text')

            phone = response.css('input[name="phoneBase64"]::attr(value)').get()
            phone = base64.b64decode(phone).decode("utf-8").replace('(','').replace(')','').replace('-','').replace(' ','')[2:]
            item.add_value('phone', phone)
        else:
            item.add_value('author', 'Unknown')
            item.add_value('phone', 'None')
        item.add_value('company', False)
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
        category = category.replace('real-estate::garage-rent', 'Гаражи и машиноместа')
        category = category.replace('real-estate::garage', 'Гаражи и машиноместа')
        item.add_value('category', category)

        item.add_value('original_url', url)
        item.add_value('created_at', 'now')
        item.add_value('processed', False)
        print('======================================================')
        return item.load_item()
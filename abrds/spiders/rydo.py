import scrapy
import datetime
import re
import requests
from scrapy.loader import ItemLoader
from scrapy.linkextractors import LinkExtractor
from abrds.items import Ad
import json
import base64

class RydoSpider(scrapy.Spider):
    name = 'rydo'
    handle_httpstatus_list = [302]
    custom_settings = {
        'COOKIES_ENABLED': False,
    }
    start_preurls = [
    #Транспорт
        'legkovye-avto',                   # Легковые автомобили
        'mototsikly',                      # Мотоциклы
    ]

    cities = [
        'moskva',               'novosibirsk',      'ekaterinburg',     'nizhniy-novgorod',
        'kazan',                'chelyabinsk',      'omsk',             'samara',
        'rostov-na-donu',       'ufa',              'krasnoyarsk',      'perm',
        'voronezh',             'volgograd',        'krasnodar',        'saratov',
        'tyumen',               'tolyatti',         'izhevsk',          'barnaul',
        'ulyanovsk',            'irkutsk',          'yaroslavl',        'vladivostok',
        'mahachkala',           'tomsk',            'orenburg',         'kemerovo',
        'ryazan',               'astrahan',         'naberezhnye-chelny', 'penza',
        'lipetsk',              'kirov',            'cheboksary',       'tula',
        'kaliningrad',          'kursk',            'sevastopol',       'ulan-ude',
        'stavropol',            'sochi',            'tver',             'ivanovo',
        'bryansk',              'belgorod',         'surgut',           'vladimir',
        'arhangelsk',           'kaluga',           'smolensk',         'saransk',
        'kurgan',               'orel',             'vologda',          'yakutsk',
        'vladikavkaz',          'groznyy',          'murmansk',         'tambov',
        'petrozavodsk',         'kostroma',         'novorossiysk',     'yoshkar-ola'
    ]
    start_urls = []
    for city in cities:
        for base_url in start_preurls:
            start_urls.append('http://rydo.ru/'+city+'/'+base_url+'/')

    # start_urls = ['http://rydo.ru/surgut/moto/prodam_pitbayk_kayo_125_2024105']
    start_urls = ['http://rydo.ru/moskva/legkovye-avto/']

    allowed_domains = ['rydo.ru']
    def __init__(self, *a, **kw):
        super(RydoSpider, self).__init__(*a, **kw)
        self.draft_category = ''

    def parse(self, response):
    # def parse_dummy(self, response):
        # Определяем список ссылок со страницы
        links = response.css('.list-element li a::attr(href)').getall()
        links = list(set(links))
        print('############# LINKS FROM PAGE ('+str(response.status)+') '+response.url+':')
        for href in links:
            page = href
            print("######################### get: "+page)
            yield response.follow(page, self.parse_item)
        # ссылки на следующие страницы
        if len(links) == 0:
            print("nothing url was found. exiting")
            return
        else:
            nextPage =  response.css('.main-next a.ui-link::attr(href)').get()
            print("######################### next page is: "+nextPage)
            yield response.follow(nextPage, self.parse)


    def parse_item(self, response):
    # def parse(self, response):
        print('------------------------------'+str(response.status)+'----------------------------------')
        print(response.url)
        item = ItemLoader(item=Ad(), response=response)
        item.add_value('provider',  'rydo')

        # actual = response.css('div[class="productPage__unactiveBlockTitle"]::text').get()
        # if actual == 'Объявление снято с публикации':
        #     actual = False
        #     item.add_value('actual', False)
        # else:
        #     actual = True
        #     item.add_value('actual', True)
        item.add_css('external_id', 'input[name="item_id"]::attr(value)')
        date = response.css('.my-breakpoint .my-detail-listview-box li::text').getall()[-1]
        date = date.replace('января', 'Jan').replace('февраля', 'Feb').replace('марта', 'Mar')
        date = date.replace('апреля', 'Apr').replace('мая', 'May').replace('июня', 'Jun')
        date = date.replace('июля', 'Jul').replace('августа', 'Aug').replace('сентября', 'Sep')
        date = date.replace('октября', 'Oct').replace('ноября', 'Nov').replace('декабря', 'Dec')
        date = datetime.datetime.strptime(date, ' Опубликовано %d %b %Y г. %H:%M').strftime('%Y-%m-%d')
        item.add_value('date', date)
        title = response.css('h1.detail_title::text').get()
        title = title[0:-4]
        item.add_value('title', title)
        item.add_css('description', '.detailprops p::text')
        item.add_css('price', 'h1 .price::text')
        item.add_css('address', 'h1 .city::text')
        # item.add_css('price_unit', '.productPage__price::attr(content)')
        
        try:
            coordinates = re.search("center: \[\d+.\d+,\d+.\d+]", response.text).group(0)
            coordinates = coordinates.replace('center: [','').replace(']','')
            coordinates = coordinates.split(',')
            item.add_value('lattitude', coordinates[0]) 
            item.add_value('longitude', coordinates[1]) 
        except BaseException:
            print('coords not found')
            item.add_value('lattitude', '0')
            item.add_value('longitude', '0')
        # images = ','.join(response.css('.lineGallery img::attr(data-src)').getall()[:10])
        # item.add_value('images', images)
        item.add_value('videos', '')

        # if actual == True:
        #     item.add_css('author', '.productPage__inlineWrapper a::text')
        #     item.add_css('author', '.productPage__infoTextBold.productPage__infoTextBold_inline::text')
        #     item.add_css('author', 'input[name="contactFace"]::attr(value)')
        #     # item.add_value('author', 'Нет имени')

        #     phone = response.css('input[name="phoneBase64"]::attr(value)').get()
        #     phone = base64.b64decode(phone).decode("utf-8").replace('(','').replace(')','').replace('-','').replace(' ','')
        #     item.add_value('phone', phone)
        # else:
        #     item.add_value('author', 'Unknown')
        #     item.add_value('phone', 'None')
        # item.add_value('company', False)
        url = response.url
        self.draft_category = re.search("rydo.ru/.*?/.*?/", url).group(0).replace('rydo.ru/','')
        self.draft_category = re.search("/.*?/", self.draft_category).group(0).replace('/','')
        # details = response.css('.productPage__infoColumnBlockText::text').getall()
        # details = self.parse_details(details, title, response.url)
        # item.add_value('details', details)

        
        try:
            if re.search("auto-", self.draft_category).group(0) != None:
                category = 'Автомобили'
        except BaseException:
            None
        if self.draft_category == 'moto':
            category = 'Мототехника'
        # category = category.replace('real-estate::rooms-sale', 'Квартиры, комнаты')
        # category = category.replace('real-estate::rooms-rent', 'Квартиры, комнаты')
        # category = category.replace('real-estate::rent', 'Квартиры, комнаты')
        # category = category.replace('real-estate::commercial-sale', 'Коммерческая недвижимость')
        # category = category.replace('real-estate::commercial', 'Коммерческая недвижимость')
        # if category == 'real-estate::out-of-town-rent':
        #     if "real-estate/out-of-town-rent/lands" in url:
        #         category = category.replace('real-estate::out-of-town-rent', 'Земельные участки')
        #     else:
        #         category = category.replace('real-estate::out-of-town-rent', 'Дома, дачи, коттеджи')
        # if category == 'real-estate::out-of-town':
        #     if "real-estate/out-of-town/lands" in url:
        #         category = category.replace('real-estate::out-of-town', 'Земельные участки')
        #     else:
        #         category = category.replace('real-estate::out-of-town', 'Дома, дачи, коттеджи')
        # category = category.replace('real-estate::out-of-town', 'Дома, дачи, коттеджи')
        # category = category.replace('real-estate::garage-rent', 'Гаражи и машиноместа')
        # category = category.replace('real-estate::garage', 'Гаражи и машиноместа')
        # category = category.replace('cars::passenger', 'Автомобили')
        # category = category.replace('cars::misc', 'Мототехника')
        # category = category.replace('cars::water', 'Водный транспорт')
        # category = category.replace('cars::commercial', 'Спецтехника')
        # category = category.replace('cars::parts', 'Запчасти для авто')

        # category = category.replace('home::garden', 'Сад и огород, дача')
        # if category == 'home::furniture-interior':
        #     if re.search('kitchen', url) != None:
        #         category = 'Посуда и товары для кухни'
        #     category = category.replace('home::furniture-interior', 'Мебель и интерьер')
        # if category == 'home::building':
        #     if re.search('instruments', url) != None:
        #         category = 'Инструменты'
        #     elif re.search('materials', url) != None:
        #         category = 'Ремонт и строительство'
        #     elif re.search('plumbing', url) != None:
        #         category = 'Ремонт и строительство'
        #     elif re.search('other', url) != None:
        #         category = 'Ремонт и строительство'
        #     elif re.search('constructions', url) != None:
        #         category = 'Ремонт и строительство'
        #     elif re.search('elements', url) != None:
        #         category = 'Ремонт и строительство'

        # category = category.replace('animals-plants::plants', 'Растения')
        # category = category.replace('business::food', 'Продукты питания')
        # category = category.replace('business::business', 'Готовый бизнес')
        # category = category.replace('business::services-business', 'Услуги')
        # category = category.replace('business::equipment', 'Оборудование для бизнеса')
        # category = category.replace('jobs-education::resumes', 'Резюме')
        # category = category.replace('jobs-education::vacancies', 'Вакансии')
        # category = category.replace('electronics-technics::tv-audio-dvd', 'Аудио и видео техника')
        # category = category.replace('electronics-technics::photo', 'Фототехника')
        # category = category.replace('electronics-technics::computers-devices', 'Компьютеры и пр.')
        # category = category.replace('electronics-technics::games', 'Игры и приставки')
        # category = category.replace('electronics-technics::kitchen', 'Бытовая техника')
        # category = category.replace('electronics-technics::vacuum', 'Бытовая техника')
        # category = category.replace('electronics-technics::washing-machines', 'Бытовая техника')
        # category = category.replace('electronics-technics::ironing-sewing-equipment', 'Бытовая техника')
        # category = category.replace('electronics-technics::climatic-technics', 'Бытовая техника')
        item.add_value('category', category)
        print(url+'/get_phone/')

        phone = requests.get(url+'/get_phone/', data={})
        print('                           '+str(phone.status_code))
        ph = phone.text
        if phone.status_code != 200 or ph == 'номер телефона не подтвержден':
            ph = 'None'
            print('Телефон не скачан')
        
        item.add_value('phone', ph)
        item.add_value('author', 'Нет имени')
        item.add_value('author_external_id', ph)

        item.add_value('original_url', url)
        item.add_value('created_at', 'now')
        item.add_value('processed', False)
        print('======================================================')
        return item.load_item()
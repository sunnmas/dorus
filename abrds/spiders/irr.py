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
    handle_httpstatus_list = [302]
    custom_settings = {
        'COOKIES_ENABLED': False,
    }
    start_preurls = [
    #Недвижимость
        'real-estate/apartments-sale',      # Продажа квартир и студий
        'real-estate/rent',                 # Аренда квартир и студий
        'real-estate/rooms-sale',           # Продажа комнат
        'real-estate/rooms-rent',           # Аренда комнат
        'real-estate/commercial-sale',      # Продажа коммерческой недвижимости
        'real-estate/commercial',           # Аренда коммерческой недвижимости
        'real-estate/out-of-town',          # Дома, коттеджи, участки продажа
        'real-estate/out-of-town-rent',     # Дома, коттеджи, участки аренда
        'real-estate/garage',               # Продажа гаражей и машиномест
        'real-estate/garage-rent',          # Аренда гаражей и машиномест
    #Транспорт
        'cars/passenger',                  # Легковые автомобили
        'cars/misc',                       # Мототехника
        'cars/water',                      # Водный транспорт
        'cars/commercial',                 # Спецтехника
        'cars/parts',                      # Запчасти для авто
    #Деловые отношения
        'business/services-business',     # Услуги
        'business/business',              # Готовый бизнес
        'business/equipment',             # Оборудование для бизнеса
        'jobs-education/resumes',         # Резюме
        'jobs-education/vacancies',       # Вакансии
    #Хозяйство
        'home/building/instruments',      # Инструменты
        'home/furniture-interior',        # Мебель и интерьер
        'home/building/materials',        # Материалы
        'home/building/plumbing',         # Сантехника
        'home/building/constructions',    # Готовые конструкции
        'home/building/other',            # Другое
        'home/building/elements',         # Двери, балконы
        'business/food',                  # Продукты питания
        'animals-plants/plants',          # Растения
        'home/garden',                    # Дача
    ]


    subdomains = [
        'saint-petersburg',     'novosibirsk',      'ekaterinburg',     'nizhniynovgorod',
        'kazan',                'chelyabinsk',      'omsk',             'samara',
        'rostovnadonu',         'ufa',              'krasnoyarsk',      'perm',
        'voronezh',             'volgograd',        'krasnodar',        'saratov',
        'tyumen',               'tolyatti',         'izhevsk',          'barnaul',
        'ulyanovsk',            'irkutsk',          'yaroslavl',        'vladivostok',
        'mahachkala',           'tomsk',            'orenburg',         'kemerovo',
        'ryazan',               'astrahan',         'nabchelny',        'penza',
        'lipetsk',              'kirov',            'cheboksary',       'tula',
        'kaliningrad',          'kursk',            'sevastopol',       'ulanude',
        'stavropol',            'sochi',            'tver',             'ivanovo',
        'bryansk',              'belgorod',         'surgut',           'vladimir',
        'arhangelsk',           'kaluga',           'smolensk',         'saransk',
        'kurgan',               'orel',             'vologda',          'yakutsk',
        'vladikavkaz',          'groznyi',          'murmansk',         'tambov',
        'petrozavodsk',         'kostroma',         'novorossiysk',     'yoshkarola'
    ]
    start_urls = []
    for subdomain in subdomains:
        for base_url in start_preurls:
            start_urls.append('https://'+subdomain+'.irr.ru/'+base_url+'/')
    for base_url in start_preurls:
        start_urls.append('https://irr.ru/'+base_url+'moskovskaya-obl/')
        start_urls.append('https://saint-petersburg.irr.ru/'+base_url+'leningradskaya-obl/')

    # start_urls = ['https://krasnoyarsk.irr.ru/real-estate/apartments-sale/secondary/prodam-2-komn-kv-61-1-kv-m-krasnoyarsk-dmitriya-advert721000118.html']

    allowed_domains = [
        'irr.ru'
    ]

    # def parse_dummy(self, response):
    def parse(self, response):
        # Определяем список ссылок со страницы
        links = response.css('.listing .listing__item .listing__itemTitleWrapper a::attr(href)').getall()
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
            try:
                cur_page_id = int(re.search('/page\d+', response.url).group(0).replace('/page',''))
                nextPage = response.url.replace('page'+str(cur_page_id)+'/','')+'page'+str(cur_page_id + 1)+'/'
            except BaseException:
                nextPage = response.url+'page2/'
            print("######################### next page is: "+nextPage)
            yield response.follow(nextPage, self.parse)


    def parse_item(self, response):
    # def parse(self, response):
        print('------------------------------'+str(response.status)+'----------------------------------')
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
        item.add_css('price_unit', '.productPage__price::attr(content)')
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
            item.add_css('author', 'input[name="contactFace"]::attr(value)')
            item.add_value('author', 'Нет имени')

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
        category = category.replace('cars::passenger', 'Автомобили')
        category = category.replace('cars::misc', 'Мототехника')
        category = category.replace('cars::water', 'Водный транспорт')
        category = category.replace('cars::commercial', 'Спецтехника')
        category = category.replace('cars::parts', 'Запчасти для авто')

        category = category.replace('home::garden', 'Сад и огород, дача')
        if category == 'home/furniture-interior':
            if re.search('kitchen', url) != None:
                category = 'Посуда и товары для кухни'
            category = category.replace('home::furniture-interior', 'Мебель и интерьер')
        if category == 'home::building':
            if re.search('instruments', url) != None:
                category = 'Инструменты'
            elif re.search('materials', url) != None:
                category = 'Ремонт и строительство'
            elif re.search('plumbing', url) != None:
                category = 'Ремонт и строительство'
            elif re.search('other', url) != None:
                category = 'Ремонт и строительство'
            elif re.search('constructions', url) != None:
                category = 'Ремонт и строительство'
            elif re.search('elements', url) != None:
                category = 'Ремонт и строительство'

        category = category.replace('animals-plants::plants', 'Растения')
        category = category.replace('business::food', 'Продукты питания')
        category = category.replace('business::business', 'Готовый бизнес')
        category = category.replace('business::services-business', 'Услуги')
        category = category.replace('business::equipment', 'Оборудование для бизнеса')
        category = category.replace('jobs-education::resumes', 'Резюме')
        category = category.replace('jobs-education::vacancies', 'Вакансии')
        item.add_value('category', category)

        item.add_value('original_url', url)
        item.add_value('created_at', 'now')
        item.add_value('processed', False)
        print('======================================================')
        return item.load_item()

    def parse_details(self, details, category, title, url):
        subs = [
                [u' м,', u','], [u' г.', u''],
                [u' сот', u''], [u' м2', u''],
                [u' км', u''], [u' л.с.', u''],
                [u'Этажей в здании', u'Этажей'],
                [u'Количество этажей', u'Этажей'],
                [u'Комнат в квартире', u'Количество комнат'],
                [u'Год постройки/сдачи', u'Год постройки'],
                [u'До метро, минут(пешком)', u'До метро пешком'],
                [u'Материал стен', u'Материал здания'],
                [u'Площадь строения', u'Общая площадь'],
                [u'Площадь арендуемой комнаты', u'Жилая площадь'],
                [u'Удаленность', u'Расстояние до города'],
                [u'Лифты в здании', u'Лифт'],
                [u'Отапливаемый', u'Отопление'],
                [u'Газ в доме', u'Газ'],
                [u'Водопровод', u'Центральное водоснабжение'],
                [u'Электричество (подведено)', u'Электричество'],
                #Автомобили
                [u'Автозапуск', u'Дистанционный запуск'],
                [u'Салон: велюровый', u'Салон: Велюр'],
                [u'Салон: кожаный', u'Салон: Кожа'],
                [u'Салон: тканевый', u'Салон: Ткань'],
                [u'Салон: кожаный', u'Салон: Кожа'],
                [u'Кол-во дверей', u'Количество дверей'],
                [u'Стеклоподъемники: передних окон', u'Электростеклоподъемники передние: 1'],
                [u'Стеклоподъемники: всех окон', u'Электростеклоподъемники передние: 1, Электростеклоподъемники задние: 1'],
                [u'Зеркала: регулировка', u'Электропривод зеркал: 1'],
                [u'Зеркала: обогрев', u'Электрообогрев зеркал: 1'],
                [u'Зеркала: регулировка и обогрев', u'Электропривод зеркал: 1, Электрообогрев зеркал: 1'],
                [u'Зеркала: регулировка и обогрев и складывание', u'Электропривод зеркал: 1, Привод складывания зеркал: 1, Электрообогрев зеркал: 1'],
                [u'Обогрев стекол: заднего и переднего', u'Электрообогрев лобового стекла: 1'],
                [u'Обогрев сидений: всех', u'Подогрев водительского сидения: 1, Подогрев пассажирского сидения: 1, Подогрев задних сидений: 1'],
                [u'Противотуманные фары', u'Противотуманные'],
                [u'Кол-во владельцев', u'Записей в ПТС'],
                [u'Кондиционер: климат-контроль', u'Климат: Климат контроль однозонный'],
                [u'Кондиционер: двухзонный', u'Климат: Климат контроль двухзонный'],
                [u'Привод: постоянный полный', u'Привод: Полный'],
                [u'Привод: подключаемый полный', u'Привод: Полный подключаемый'],
                [u'Тип кузова: хэтчбек', u'Кузов: Хетчбэк'],
                [u'Тип двигателя: газ', u'Газ'],
                [u'Тип трансмиссии: автомат', u'Трансмиссия: Автоматическая'],
                [u'Тип трансмиссии: механика', u'Трансмиссия: Механическая'],
                [u'Тип трансмиссии: вариатор', u'Трансмиссия: Вариатор'],
                [u'Тип трансмиссии: робот', u'Трансмиссия: Роботизированная'],
                [u'Состояние автомобиля: б/у', u'Б/у'],
                [u'Состояние автомобиля: битый', u'Битый'],
                [u'Усилитель руля (ГУР): гидроусилитель', u'Усилитель руля: Гидро'],
                [u'Объем двигателя', u'Объем'],
                [u'Фары: биксенон', u'Тип фар: Биксеноновые'],
                [u'Фары: галогеновые', u'Тип фар: Галогенные'],
                [u'Таможня: растаможен', u'Растаможен'],
                [u'Таможня: не растаможен', u'Растаможен: 0'],
                [u'Люк: электро', u'Люк'],
                [u'Люк: механика', u'Люк'],
                [u'Спутниковая сигнализация', u'Спутник'],
                [u'Handsfree', u'Hands free'],
                [u'Телевизор', u'TV'],
                [u'ABS', u'Антиблокировочная система'],
                [u'ESP', u'Курсовая устойчивость'],
                [u'EBD', u'Распределение тормозных усилий']
            ]
        result = []
        print('draft details: '+'='.join(details))
        for i in details:
            for k in subs:
                i = i.replace(k[0], k[1])
            if re.search(': ', i) == None:
                i = i + ': 1'
            result.append('"'+i.strip().replace(': ','": "', 15)+'"')
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
                result.append('"Тип жилья": "Вторичное жилье"')
            else:
                result.append('"Тип жилья": "Новостройка"')

        if (category == 'real-estate::rooms-sale') or (category == "real-estate::rooms-rent"):
            result.append('"Тип квартиры": "Комната"')
        if (category == 'real-estate::apartments-sale') or (category == "real-estate::rent"):
            result.append('"Тип квартиры": "Квартира"')
        result = '{'+', '.join(result)+'}'

        print("details: "+result)
        return result
import scrapy
import re
import requests
import datetime
from scrapy.loader import ItemLoader
from scrapy.linkextractors import LinkExtractor
from abrds.items import Ad
import json

class DorusSpider(scrapy.Spider):
    name = 'dorus'
    custom_settings = {
        'COOKIES_ENABLED': False,
        'CONCURRENT_REQUESTS': 1,
        'DOWNLOAD_TIMEOUT': 135,
        'AUTOTHROTTLE_MAX_DELAY': 900,
        'AUTOTHROTTLE_START_DELAY': 80,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 1
    }
    start_urls = [
        'http://russia.dorus.ru/auto/renovation/',
        'http://russia.dorus.ru/auto/buses/',
        'http://russia.dorus.ru/auto/boats/',
        'http://russia.dorus.ru/auto/trucks/',
        'http://russia.dorus.ru/auto/rail/',
        'http://russia.dorus.ru/auto/spares/',
        'http://russia.dorus.ru/auto/cars/',
        'http://russia.dorus.ru/auto/moto/',
        'http://russia.dorus.ru/auto/rent/',

        'http://russia.dorus.ru/business/sales/',
        'http://russia.dorus.ru/business/services/',

        'http://russia.dorus.ru/electronics/audio-video/',
        'http://russia.dorus.ru/electronics/game-consoles/',
        'http://russia.dorus.ru/electronics/vacuum/',
        'http://russia.dorus.ru/electronics/washing/',
        'http://russia.dorus.ru/electronics/televisions/',
        'http://russia.dorus.ru/electronics/refrigerators/',
        'http://russia.dorus.ru/electronics/repair/',
        'http://russia.dorus.ru/electronics/home-appliances/',
        'http://russia.dorus.ru/electronics/photo/',
        'http://russia.dorus.ru/electronics/telephones/',

        'http://russia.dorus.ru/computers/accessories/',
        'http://russia.dorus.ru/computers/computers/',
        'http://russia.dorus.ru/computers/laptops/',
        'http://russia.dorus.ru/computers/office-equipment/',
        'http://russia.dorus.ru/computers/pda/',
        'http://russia.dorus.ru/computers/reconditioning/',

        'http://russia.dorus.ru/beast/dogs/',
        'http://russia.dorus.ru/beast/cats/',
        'http://russia.dorus.ru/beast/birds/',
        'http://russia.dorus.ru/beast/products/',
        'http://russia.dorus.ru/beast/flowers/',
        'http://russia.dorus.ru/beast/houseplants/',

        'http://russia.dorus.ru/health/weight-loss/',
        'http://russia.dorus.ru/health/cosmetics/',
        'http://russia.dorus.ru/health/beauty/',
        'http://russia.dorus.ru/health/cosmetology/',
        'http://russia.dorus.ru/health/massage/',
        'http://russia.dorus.ru/health/accommodation/',
        'http://russia.dorus.ru/health/traditional/',
    ]

    allowed_domains = [
        'dorus.ru'
    ]

    proxyDict = { 
        'http': '127.0.0.1:8118'
    }
    # start_urls = [
    #     'http://www.dorus.ru/auto/renovation/regulirovka-sveta-far_9105541.html',
    #     'http://www.dorus.ru/auto/renovation/remont-radiatorov-ohlazhdeniya-interkulerov_14558985.html',
    #     'http://www.dorus.ru/auto/renovation/shinomontazh-za-999_15263293.html',
    #     'http://www.dorus.ru/auto/renovation/stellazhi-dlya-shin-koles-diskov-pokryshek_12794232.html',
    #     'http://www.dorus.ru/auto/rail/novye-poluvagony_15259249.html',
    #     'http://www.dorus.ru/auto/rail/predostavlenie-zheleznodorozhnyh-vagonov-v-arendu_15214084.html',
    #     'http://www.dorus.ru/auto/rail/vozmem-v-dlitelnuyu-arendu-krytye-vagony-i_15213923.html',
    #     'http://www.dorus.ru/auto/rail/priobretaem-b-u-vagony-tsisterny-gruzovye-i-pass_14724387.html',
    #     'http://www.dorus.ru/auto/cars/pajeroio-1998-240000ki_12304926.html',
    #     'http://www.dorus.ru/auto/cars/prodazha-henday-stareks_15261748.html',
    #     'http://www.dorus.ru/auto/cars/prodaetsya-vaz-2104-v-otlichnom-sostoyanii_15259938.html',
    #     'http://www.dorus.ru/auto/cars/gaz-3110_7479495.html',
    # ]

    def parse(self, response):
    # def parse_dummy(self, response):
        links = response.xpath('///div[@class="onepost"]//a/@href').getall()
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
                nextPage = response.url.replace('page'+str(cur_page_id)+'.html','')+'page'+str(cur_page_id + 1)+'.html'
            except BaseException:
                nextPage = response.url.replace('.html', '')+'page2.html'
            print("######################### next page is: "+nextPage)
            yield response.follow(nextPage, self.parse)

    def parse_item(self, response):
    # def parse(self, response):
        print('------------------------------'+str(response.status)+'----------------------------------')
        print(response.url)
        # print(response.text)
        item = ItemLoader(item=Ad(), response=response)
        id = re.search('\d+.html', response.url).group(0).replace('.html','')
        item.add_value('external_id', id)

        phone = requests.post("http://www.dorus.ru/action.php", data={'act': 'getcontact', 'type': 'phone', 'id': id}, proxies=self.proxyDict)
        if phone.status == 200:
            item.add_value('phone', phone.text)
        else:
            raise Exception('Номер телефона не скачан. Код ответа: '+str(phone.status))

        item.add_value('author_external_id', phone)
        item.add_css('author', 'div.pauthor::text')
        item.add_value('company', False)
        item.add_css('title', 'h1::text')
        item.add_css('description', 'div.margt6.margb12::text')
        item.add_css('price', 'div.pprice::text')
        item.add_value('price_unit', '₽')
        item.add_value('videos', '')
        item.add_value('details', '')
        item.add_css('site', 'div.purl>span::text')
        item.add_value('lattitude', '0')
        item.add_value('longitude', '0')
        item.add_css('address', 'div.pcity::text')

        date = response.xpath('//script/text()').re('Дата размещения: .+:\d\d</div>')[0].replace("Дата размещения: ", "").replace("</div>", "")
        date = date.replace('Января', 'Jan').replace('Февраля', 'Feb').replace('Марта', 'Mar')
        date = date.replace('Апреля', 'Apr').replace('Мая', 'May').replace('Июня', 'Jun')
        date = date.replace('Июля', 'Jul').replace('Августа', 'Aug').replace('Сентября', 'Sep')
        date = date.replace('Октября', 'Oct').replace('Ноября', 'Nov').replace('Декабря', 'Dec')
        date = str(datetime.datetime.now().year)+'-'+datetime.datetime.strptime(date, '%d %b %Y года, %H:%M').strftime('%m-%d %H:%M:00')
        item.add_value('date', date)

        images = ','.join(response.css('div.imgfull img::attr(src)').extract())
        item.add_value('images', images)

        category = response.css('div.bullet.fbold span::text').get()
        category = category.replace('Автосервис и ремонт', 'Услуги')
        category = category.replace('Автобусы, микроавтобусы', 'Спецтехника')
        category = category.replace('Грузовые автомобили', 'Спецтехника')
        category = category.replace('Железнодорожный транспорт', 'Спецтехника')
        category = category.replace('Запчасти и аксессуары', 'Запчасти для авто')
        category = category.replace('Легковые автомобили', 'Автомобили')
        category = category.replace('Мотоциклы, мопеды', 'Мототехника')
        category = category.replace('Прокат автомобилей', 'Автомобили')

        category = category.replace('Продажа и покупка бизнеса', 'Готовый бизнес')
        category = category.replace('Услуги по бизнесу', 'Готовый бизнес')

        category = category.replace('Игровые приставки', 'Игры и приставки')
        category = category.replace('Пылесосы', 'Бытовая техника')
        category = category.replace('Телевизоры', 'Бытовая техника')
        category = category.replace('Холодильники', 'Бытовая техника')
        category = category.replace('Техника для дома', 'Бытовая техника')
        category = category.replace('Фотоаппараты', 'Фототехника')
        category = category.replace('Ремонт электроники', 'Услуги')
        category = category.replace('Телефоны', 'Мобильные устройства')
        category = category.replace('Планшеты', 'Мобильные устройства')
        category = category.replace('Комплектующие', 'Компьютеры и пр.')
        category = category.replace('Компьютеры', 'Компьютеры и пр.')
        category = category.replace('Ноутбуки', 'Компьютеры и пр.')
        category = category.replace('Оргтехника', 'Компьютеры и пр.')
        category = category.replace('Ремонт и сервис', 'Компьютеры и пр.')

        category = category.replace('Собаки и щенки', 'Собаки')
        category = category.replace('Кошки и котята', 'Кошки')
        category = category.replace('Цветы', 'Растения')
        category = category.replace('Растения комнатные', 'Растения')

        category = category.replace('Коррекция фигуры и веса', 'Красота и здоровье')
        category = category.replace('Косметика и парфюмерия', 'Красота и здоровье')
        category = category.replace('Косметические услуги', 'Услуги')
        category = category.replace('Лечебная косметология', 'Красота и здоровье')
        category = category.replace('Массаж', 'Услуги')
        category = category.replace('Медицинские услуги', 'Услуги')
        category = category.replace('Услуги народной медицины', 'Услуги')

        item.add_value('category', category)

        item.add_value('actual', True)
        item.add_value('original_url', response.url)
        item.add_value('created_at', 'now')
        item.add_value('processed', False)
        item.add_value('provider',  'dorus')
        print('======================================================')
        return item.load_item()
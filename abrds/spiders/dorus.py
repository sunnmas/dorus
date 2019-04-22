import scrapy
import re
import requests

class QuotesSpider(scrapy.Spider):
    name = 'dorus'
    start_urls = [
        'http://russia.dorus.ru/auto/buses'
    ]

    allowed_domains = [
        'dorus.ru'
    ]

    def parse(self, response):
        # follow links to adv pages
        for href in response.xpath('///div[@class="onepost"]//a/@href').getall():
            yield response.follow(href, self.parse_item)
        # follow pagination links
        nextPage = response.xpath('///div[@class="margt24"]/span[@class="link"]/@onclick').get().replace("openLink('",'').replace("', true)",'')
        yield response.follow(nextPage, self.parse)

    def parse_item(self, response):
        id = re.findall('\d+', response.xpath('//script/text()').re('Номер этого объявления: [\d]+</div>')[0])[0]
        r = requests.post("http://www.dorus.ru/action.php", data={'act': 'getcontact', 'type': 'phone', 'id': id})
        phone = r.text

        result = {
            'provider': 'dorus',
            'external_id': id,
            'date': response.xpath('//script/text()').re('Дата размещения: .+:\d\d</div>')[0].replace("Дата размещения: ", "").replace("</div>", ""),
            'title': response.css('h1::text').get(),
            'description': response.css('div.margt6.margb12::text').get(),
            'price': response.css('div.pprice::text').re('\d+')[0],
            'address': response.css('div.pcity::text').get().replace("Город: ", ""),
            'coordinates': None,
            'ext_category':  response.css('div.bullet.fbold span::text').get(),
            'images': response.css('div.imgfull img::attr(src)').extract(),
            'videos': None,
            'site': None,
            'details': None,
            'author_external_id': 'unknown id',
            'author': response.css('div.pauthor::text').get().replace("Контактное лицо: ", ""),
            'phone': phone,
            'original_url': response.css('div.purl span::text').get(),
        }

        yield result
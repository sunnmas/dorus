import scrapy
import re
import requests

class QuotesSpider(scrapy.Spider):
    name = 'dorus'
    start_urls = [
        'http://www.dorus.ru/computers/office-equipment/jc97-03220a-003n01018-kronshteyn-avtopodatchika_10380288.html',
    ]

    def parse(self, response):
        # for quote in response.css('div.quote'):
        r = requests.post("http://www.dorus.ru/action.php", data={'act': 'getcontact', 'type': 'phone', 'id': '10380288'})
        phone = r.text

        result = {
            'external_id': re.findall('\d+', response.xpath('//script/text()').re('Номер этого объявления: [\d]+</div>')[0])[0],
            'title': response.css('h1::text').get(),
            'price': response.css('div.pprice::text').get(),
            'author': response.css('div.pauthor::text').get(),
            'city': response.css('div.pcity::text').get(),
            'date': response.xpath('//script/text()').re('Дата размещения: .+:\d\d</div>'),
            'images': response.css('div.imgfull img::attr(src)').extract(),
            'phone': phone
        }
        # phone_request = FormRequest.from_response("http://www.dorus.ru/action.php", callback=parse_phone, formdata={'act': 'getcontact', 'id': '10380288', 'type': 'phone'})


        yield result

        # type = 'phone'
        # var data = 'act=getcontact&id=' + id + '&type=' + type;
        # req.open('POST', 'http://' + city + '.dorus.ru/action.php', true);
        #     req.setRequestHeader('Accept-Charset', 'windows-1251');
        #     req.setRequestHeader('Accept-Language','ru, en');
        #     req.setRequestHeader('Connection', 'close');
        #     req.setRequestHeader('Content-length', data.length);
        #     req.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');

        next_page = None
        # response.css('li.next a::attr("href")').get()
        if next_page is not None:
            yield response.follow(next_page, self.parse)
    # def parse_phone(self,response):
    #     result['phone'] = phone_request
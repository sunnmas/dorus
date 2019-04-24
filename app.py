from scrapy.crawler import CrawlerProcess
from abrds.spiders.cmlt import CmltSpider

if __name__ == '__main__':
    process = CrawlerProcess()

    process.crawl(CmltSpider)
    process.start() # the script will block here until the crawling is finished
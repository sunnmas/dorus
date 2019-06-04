import scrapy
from scrapy.crawler import CrawlerProcess
from abrds.spiders.irr import IrrSpider

if __name__ == '__main__':
    process = CrawlerProcess()

    process.crawl(IrrSpider)
    process.start() # the script will block here until the crawling is finished
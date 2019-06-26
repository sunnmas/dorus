import scrapy
from scrapy.crawler import CrawlerProcess
from abrds.spiders.irr import PhtdskSpider
from scrapy.utils.project import get_project_settings

settings = get_project_settings()
process = CrawlerProcess(settings)
process.crawl(PhtdskSpider)
process.start() # the script will block here until the crawling is finished
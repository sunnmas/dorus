import scrapy
from scrapy.crawler import CrawlerProcess
from abrds.spiders.irr import IrrSpider
from abrds.spiders.cmlt import CmltSpider
from scrapy.utils.project import get_project_settings

settings = get_project_settings()
process = CrawlerProcess(settings)
process.crawl(IrrSpider)
# process.crawl(CmltSpider)
process.start() # the script will block here until the crawling is finished
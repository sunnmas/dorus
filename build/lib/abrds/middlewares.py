# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
import re

class AbrdsSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class AbrdsDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)

#================================================================================

import os
import sys
import random
# try:
#     from scrapy.conf import settings
# except:
#     from scrapy.crawler import settings
from scrapy.utils.project import get_project_settings
from toripchanger import TorIpChanger

# A Tor IP will be reused only after 10 different IPs were used.
ip_changer = TorIpChanger(reuse_threshold=10)


class RandomUserAgentMiddleware(object):
    def process_request(self, request, spider):
        settings = get_project_settings()
        ua  = random.choice(settings.get('USER_AGENT_LIST'))
        if ua:
            request.headers.setdefault('User-Agent', ua)

class ProxyMiddleware(object):
    _requests_count = 0

    def process_request(self, request, spider):
        settings = get_project_settings()
        use_tor = settings.get('USE_TOR')
        if use_tor:
            self._requests_count += 1
            if self._requests_count > 111:
                self._requests_count = 0 
                ip_changer.get_new_ip()
            try:
                proxy = str(sys.argv[1])
                if re.match('tor:', proxy) == None:
                    proxy = str(sys.argv[2])
                    if re.match('tor:', proxy) == None:
                        proxy = str(sys.argv[3])
                        if re.match('tor:', proxy) == None:
                            proxy = str(sys.argv[4])
                            if re.match('tor:', proxy) == None:
                                raise Exception("There no tor proxy")
                proxy = proxy.replace('tor:','')
            except:
                proxy = settings.get('HTTP_PROXY')

            request.meta['proxy'] = proxy
            spider.log('proxy: %s' % request.meta['proxy'])
        else: 
            spider.log('parsing without TOR!!')
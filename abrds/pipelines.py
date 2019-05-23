# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import sys
import pymysql.cursors
import hashlib
from scrapy.exceptions import DropItem
from scrapy.http import Request

class MysqlStore(object):
    def __init__(self):
        print("PIPELINE INIT")


    def process_item(self, item, spider):    
        print("STORE TO MYSQL")
        connection = pymysql.connect(host='62.33.3.10',
                             user='spider',
                             password='dgfjghjdghdfh',
                             db='scrapy',
                             charset="utf8",
                             cursorclass=pymysql.cursors.DictCursor)
        # try:

        with connection.cursor() as cursor:
            # Read a single record
            sql = """INSERT INTO items (
                            provider, external_id, date,
                            title, description, price, address,
                            coordinates, category,
                            images, videos, site, details,
                            author_external_id, author,
                            phone, original_url)  
                    VALUES (%s, %s, %s, %s, %s, %s, %s, POINT(%s,%s), %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

            params = (
                        item['provider'], 
                        item['external_id'],
                        item['date'],
                        item['title'],
                        item['description'],
                        item['price'],
                        item['address'],
                        item['lattitude'],
                        item['longitude'],
                        item['category'],
                        item['images'],
                        item['videos'],
                        item['site'],
                        item['details'],
                        item['author_external_id'],
                        item['author'],
                        item['phone'],
                        item['original_url']
                     )
            print(params)
            cursor.execute(sql, params)
        connection.commit()
            # print(result)
        # except MySQLdb.Error as e:
            # print("Error %d: %s" % (e.args[0], e.args[1]))
        # finally:
        connection.close()

        return item
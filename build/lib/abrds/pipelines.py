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
import re

class MysqlStore(object):
    def __init__(self):
        print("PIPELINE INIT")

        try:
            self.mysql_host = str(sys.argv[1])
            if re.match('mysql:', self.mysql_host) == None:
                self.mysql_host = str(sys.argv[2])
                if re.match('mysql:', self.mysql_host) == None:
                    self.mysql_host = str(sys.argv[3])
                    if re.match('mysql:', self.mysql_host) == None:
                        self.mysql_host = str(sys.argv[4])
                        if re.match('mysql:', self.mysql_host) == None:
                            raise Exception("There no mysql host")
            self.mysql_host = self.mysql_host.replace('mysql:','')
        except:
            self.mysql_host = '172.10.0.6'
        print('Mysql host:', self.mysql_host)

        self.rejected_authors = [
            'Ауди Авилон',          'Звезда Столицы Варшавка',
            'Ауди Центр Юг',        'Звезда Столицы Каширка',
            'Ауди Центр Россия',    'Jeep Авилон'
        ]

    def process_item(self, item, spider):
        item.setdefault('author', 'Нет имени')
        if item['author'] in self.rejected_authors:
            print('author rejected: '+item['author'])
            return

        try:
            mysql_host = str(sys.argv[1])
        except:
            mysql_host = '172.10.0.6'
        spider.log("STORE TO MYSQL on "+self.mysql_host)   
        connection = pymysql.connect(host=self.mysql_host,
                             user='spider',
                             password='dfjglihdbvpguwpy04hbvdhvciudnvl',
                             db='scrapy',
                             charset="utf8",
                             cursorclass=pymysql.cursors.DictCursor)

        with connection.cursor() as cursor:
            params = [
                        item['provider'], 
                        item['external_id'],
                        item['date'],
                        item['title'],
                        item['description'],
                        item['price'],
                        item['price_unit'],
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
                        item['company'],
                        item['phone'],
                        item['original_url'],
                        item['actual']
                     ]
            editable_params = [
                        item['date'],
                        item['title'],
                        item['description'],
                        item['price'],
                        item['price_unit'],
                        item['address'],
                        item['lattitude'],
                        item['longitude'],
                        item['images'],
                        item['videos'],
                        item['site'],
                        item['details'],
                        item['phone'],
                        item['actual']
                     ]
            select_condition = [
                        item['provider'],
                        item['external_id']
                    ]
            print("params:")
            print(params)
            sql = "SELECT external_id FROM items WHERE provider=%s AND external_id=%s"
            cursor.execute(sql, select_condition)
            result = cursor.fetchone()
            print(result)
            if result:
                print('update existing record..')
                if item['actual'][0] == True:
                    sql = "UPDATE items SET date=%s, title=%s, description=%s, price=%s, price_unit=%s, address=%s, coordinates=POINT(%s,%s), images=%s, videos=%s, site=%s, details=%s, phone=%s, actual=%s, processed=0, updated_at=NOW() WHERE provider=%s AND external_id=%s"
                    print(sql)
                    result = cursor.execute(sql, editable_params+select_condition)
                else:
                    sql = "UPDATE items SET actual=0, processed=0, updated_at=NOW() WHERE provider=%s AND external_id=%s"
                    print(sql)
                    result = cursor.execute(sql, select_condition)
                print(result)
            else:
                print('insert new record..')
                sql = """INSERT INTO items (
                            provider, external_id, date,
                            title, description, price, price_unit, address,
                            coordinates, category,
                            images, videos, site, details,
                            author_external_id, author, company,
                            phone, original_url, actual)  
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, POINT(%s,%s), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                print(sql)
                cursor.execute(sql, params)
                print('inserted')

            connection.commit()
            connection.close()
        #end with connection.cursor()

        return item
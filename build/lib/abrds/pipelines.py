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
        try:
            self.mysql_host = str(sys.argv[1])
            if self.mysql_host == 'irr':
                raise Exception("There no mysql host")
        except:
            self.mysql_host = '172.10.0.6'
        print('Mysql host:', self.mysql_host)


    def process_item(self, item, spider):
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
        # try:
        with connection.cursor() as cursor:
            params = [
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
                     ]
            editable_params = [
                        item['date'],
                        item['title'],
                        item['description'],
                        item['price'],
                        item['address'],
                        item['lattitude'],
                        item['longitude'],
                        item['images'],
                        item['videos'],
                        item['site'],
                        item['details'],
                        item['phone']
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
                sql = "UPDATE items SET date=%s, title=%s, description=%s, price=%s, address=%s, coordinates=POINT(%s,%s), images=%s, videos=%s, site=%s, details=%s, phone=%s, processed=0, updated_at=NOW() WHERE provider=%s AND external_id=%s"
                print(sql)
                result = cursor.execute(sql, editable_params+select_condition)
                print(result)
            else:
                print('insert new record..')
                sql = """INSERT INTO items (
                            provider, external_id, date,
                            title, description, price, address,
                            coordinates, category,
                            images, videos, site, details,
                            author_external_id, author,
                            phone, original_url)  
                    VALUES (%s, %s, %s, %s, %s, %s, %s, POINT(%s,%s), %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                print(sql)
                cursor.execute(sql, params)
                print('inserted')

            connection.commit()
            connection.close()

                # print(result)
        # except MySQLdb.Error as e:
        #     print("Error %d: %s" % (e.args[0], e.args[1]))
        # finally:

        return item
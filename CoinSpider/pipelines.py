# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo
from CoinSpider.items import *


class MongoDBPipeline(object):
    def __init__(self):
        client = pymongo.MongoClient("localhost", 27017)
        db = client["Coins"]
        self.CoinUrl = db["CoinUrl"]
        self.Coin = db["Coin"]

    def process_item(self, item, spider):
        """ 判断item的类型，并作相应的处理，再入数据库 """
        if isinstance(item, Coin):
            try:
                count = self.Coin.find({'english_name': item['english_name']}).count()
                if count > 0:
                    self.Coin.update({'english_name': item['english_name']}, dict(item))
                else:
                    self.Coin.insert(dict(item))
            except Exception as e:
                print(e)
                pass
        elif isinstance(item, CoinUrl):
            try:
                count = self.CoinUrl.find({'name': item['name']}).count()
                if count > 0:
                    self.CoinUrl.update({'name': item['name']}, dict(item))
                else:
                    self.CoinUrl.insert(dict(item))
            except Exception as e:
                print(e)
                pass

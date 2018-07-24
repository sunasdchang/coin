import re
import json
import time
import requests
import logging
from scrapy import Spider, Selector
from scrapy.http import Request
from CoinSpider.items import *
from datetime import datetime
from django.utils.timezone import utc
from CoinSpider.util import Tool

base_url = 'http://www.feixiaohao.com'


class CoinSpider(Spider):
    name = 'CoinSpider'
    allowed_domains = ['feixiaohao.com']
    start_urls = [
        'http://www.feixiaohao.com/all/'
    ]
    logging.getLogger("requests").setLevel(logging.WARNING)  # 将requests的日志级别设成WARNING
    tool = Tool()

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url=url, callback=self.parse_coin)

    def parse_coin(self, response):
        selector = Selector(response)
        items = selector.xpath('//div[@class="boxContain"]/table/tbody/tr/td/a').extract()
        for item in items:
            urls = re.findall(r'<a href="(.*?)" target="_blank">.*? alt="(.*?)">', item, re.S)
            if len(urls) > 0:
                print(urls[0][0])
                print(urls[0][1])
                coin_url = CoinUrl()
                coin_url['url'] = base_url + urls[0][0]
                coin_url['name'] = urls[0][1]
                print('==========================================')
                yield coin_url

                # sleep 5s in order to avoid seal ip
                time.sleep(5)
                yield Request(url=base_url + urls[0][0], callback=self.parse_coin_detail_info)

        # test
        # yield Request(url='http://www.feixiaohao.com/currencies/zsecoin/', callback=self.parse_coin_detail_info)

    def parse_coin_detail_info(self, response):
        selector = Selector(response)
        coin = Coin()

        # current price 当前价格数据
        coin_price = selector.xpath('//div[@class="coinprice"]').extract()
        current_price = re.findall(r'<div class="coinprice">(.*?)<span', coin_price[0], re.S)
        if len(current_price) is not 0:
            coin['price'] = current_price[0]
            coin['time'] = datetime.utcnow().replace(tzinfo=utc)
            print(coin['price'], ' ', coin['time'])

        # lowest price and highest price最高和最低价格数据
        low_height = selector.xpath('//div[@class="lowHeight"]').extract()
        prices = re.findall(r'<div class="lowHeight">.*?<span class="value">(.*?)</span></div>.*?<div>.*?<span class="value">(.*?)</span></div>', low_height[0], re.S)
        if len(prices) is not 0:
            coin['highest_price'] = prices[0][0]
            coin['lowest_price'] = prices[0][1]
            print(coin['highest_price'], ' ', coin['lowest_price'])

        # description币的描述数据
        desc = selector.xpath('//div[@class="des"]/a').extract()
        description = re.findall(r'<a href="(.*?)" target="_blank">', desc[0], re.S)
        if len(description) is not 0:
            desc_url = base_url + description[0]
            print(desc_url)
            response = requests.get(desc_url)
            desc_selector = Selector(response)
            desc_content = desc_selector.xpath('//div[@class="boxContain"]/div/p').extract()
            coin['description'] = self.tool.replace(''.join(i.strip() for i in desc_content))
            print(coin['description'])

        # market市场相关信息
        market = selector.xpath('//div[@id="baseInfo"]/div[@class="firstPart"]/div/div[@class="value"]').extract()
        values = []
        for value in market:
            market_value = re.findall(r'<div class="value">(.*?)<', value, re.S)
            values.append(market_value[0])

        if len(values) is not 0:
            coin['market_capitalization'] = values[0]  # 流通市值
            coin['market_count'] = values[1]           # 流通量
            coin['publish_count'] = values[2]          # 发行量
            coin['tx_count'] = values[3]               # 交易额
            print(coin['market_capitalization'], ' ', coin['market_count'], ' ', coin['publish_count'], ' ', coin['tx_count'])

        # base info列表基本信息数据
        items = selector.xpath('//div[@id="baseInfo"]/div[@class="secondPark"]/ul/li').extract()
        for item in items:
            base_info = re.findall(r'<li>.*?<span class="tit">(.*?)</span>.*?<span class="value">(.*?)</span>.*?</li>', item, re.S)
            if len(base_info) is not 0:
                if base_info[0][0] == '英文名：':
                    coin['english_name'] = self.tool.replace(base_info[0][1]).strip()
                    print(coin['english_name'])
                elif base_info[0][0] == '中文名：':
                    coin['chinese_name'] = self.tool.replace(base_info[0][1]).strip()
                    print(coin['chinese_name'])
                elif base_info[0][0] == '上架交易所：':
                    coin['exchanger_count'] = self.tool.replace(base_info[0][1]).strip()
                    print(coin['exchanger_count'])
                elif base_info[0][0] == '发行时间：':
                    coin['publish_time'] = self.tool.replace(base_info[0][1]).strip()
                    print(coin['publish_time'])
                elif base_info[0][0] == '白皮书：':
                    coin['white_paper'] = self.tool.replace(base_info[0][1]).strip()
                    print(coin['white_paper'])
                elif base_info[0][0] == '网站：':
                    websites = re.findall(r'<a href="(.*?)" rel="nofollow" target="_blank">', base_info[0][1], re.S)
                    if len(websites) is not 0:
                        office_websites = []
                        for website in websites:
                            office_websites.append(self.tool.replace(website).strip())
                        coin['website'] = office_websites
                        print(coin['website'])
                elif base_info[0][0] == '区块站：':
                    explorers = []
                    block_explorers = re.findall(r'<a href="(.*?)" rel="nofollow" target="_blank">', base_info[0][1], re.S)
                    if block_explorers is not []:
                        for block_explorer in block_explorers:
                            explorers.append(self.tool.replace(block_explorer).strip())
                        coin['block_explorer'] = explorers
                        print(coin['block_explorer'])
                elif base_info[0][0] == '是否代币：':
                    coin['is_token'] = self.tool.replace(base_info[0][1]).strip()
                    print(coin['is_token'])
                elif base_info[0][0] == '众筹价格：':
                    ico_price = re.findall(r'<a href="#ico">(.*?)</a>', base_info[0][1], re.S)
                    coin['ico_price'] = self.tool.replace(ico_price[0]).strip()
                    print(coin['ico_price'])

        yield coin


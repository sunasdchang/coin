# -*- coding: utf-8 -*-
# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
import os
import random
import json
import logging
import time
from scrapy.exceptions import IgnoreRequest
from scrapy.utils.response import response_status_message
from scrapy.downloadermiddlewares.retry import RetryMiddleware

logger = logging.getLogger(__name__) #日志输出


class UserAgentMiddleware(object):
    """
    换User-Agent
    """

    def process_request(self, request, spider):
        # agent = random.choice(agents)
        # request.headers["User-Agent"] = agent
        pass


class CookiesMiddleware(RetryMiddleware):
    """
    维护Cookie
    """

    def process_request(self, request, spider):
        pass

    def process_response(self, request, response, spider):
        if response.status in [300, 301, 302, 303]:
            try:
                redirect_url = response.headers["location"]
                if "login.weibo" in redirect_url or "login.sina" in redirect_url:  # Cookie失效
                    logger.warning("One Cookie need to be updating...")
                elif "weibo.cn/security" in redirect_url:  # 账号被限
                    logger.warning("One Account is locked! Remove it!")
                elif "weibo.cn/pub" in redirect_url:
                    logger.warning(
                        "Redirect to 'http://weibo.cn/pub'!( Account:%s )" % request.meta["accountText"].split("--")[0])
                reason = response_status_message(response.status)
                time.sleep(5)
                return self._retry(request, reason, spider) or response  # 重试
            except Exception as e:
                raise IgnoreRequest
        elif response.status in [403, 414]:
            logger.error("%s! Stopping..." % response.status)
            os.system("pause")
        else:
            return response

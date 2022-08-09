# encoding = utf-8
import json
import re
import urllib.parse

import mitmproxy.http
import requests
import concurrent.futures as futures


class Counter:

    def __init__(self):
        self.data = {}
        self.tp = futures.ThreadPoolExecutor(10)

    def request(self, flow: mitmproxy.http.HTTPFlow):
        # ctx.log.info('白色标准输出:{}'.format(flow.request.url))
        # ctx.log.warn('黄色警告输出:{}'.format(flow.request.url))
        # ctx.log.error('红色异常输出:{}'.format(flow.request.url))
        print('')

    def response(self, flow: mitmproxy.http.HTTPFlow):
        # 获取网页状态码
        real_url = urllib.parse.unquote(flow.request.url, encoding='utf-8')

        if real_url.__contains__('dtliving-sh.dingtalk.com/live_hp') and real_url.__contains__('args_url'):
            real_url = real_url.replace('\\', '')
            args_feed_id = re.search(r'args_feed_id":"(?P<args_feed_id>.*?)"', real_url).group('args_feed_id')
            args_url = re.search(r'args_url":"(?P<args_url>.*?)"', real_url).group('args_url')
            if args_feed_id not in self.data.keys():
                self.data[args_feed_id] = {
                    'm3u8_url': 'https:' + args_url
                }
            else:
                self.data[args_feed_id]['m3u8_url'] = args_url

            self.tp.submit(self.push)
        # # 写入文件
        # with open('软考/dingding.txt', 'a', encoding='utf-8') as f:
        #     f.write(json.dumps(self.data, ensure_ascii=False) + '\n')

        if real_url.__contains__('retcode.taobao.com') and real_url.__contains__('liveInfo'):
            json_str = re.search(r'\[response\](?P<reponse>{.*})', real_url).group('reponse')
            response = json.loads(json_str)

            live_info = response['liveInfo']
            title = live_info['title']
            url = response['liveUrlHls']
            args_feed_id = re.search(r'(?P<args_feed_id>.*).m3u8', url.split('/')[-1]).group('args_feed_id')
            if args_feed_id not in self.data.keys():
                self.data[args_feed_id] = {
                    'title': title
                }
            else:
                self.data[args_feed_id]['title'] = title

    def push(self):
        requests.post('http://localhost:5000/push', json=self.data)


addons = [
    Counter()
]

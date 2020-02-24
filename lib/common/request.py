import asyncio
import functools
import config
import aiohttp
from aiohttp import ClientSession
from bs4 import BeautifulSoup
import random


class Request:
    def __init__(self, target, port, output):
        self.target = target
        self.port = port
        self.output = output
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.run())
        self.output.newLine("OK")

    def get_headers(self):
        """
        生成伪造请求头
        """
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
            'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/68.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:61.0) '
            'Gecko/20100101 Firefox/68.0',
            'Mozilla/5.0 (X11; Linux i586; rv:31.0) Gecko/20100101 Firefox/68.0']
        ua = random.choice(user_agents)
        headers = {
            'Accept': 'text/html,application/xhtml+xml,'
                      'application/xml;q=0.9,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'DNT': '1',
            'Referer': 'https://www.google.com/',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': ua,
        }
        return headers

    def get_title(self, markup):
        """
        获取标题
        :param markup: html标签
        :return: 标题
        """
        soup = BeautifulSoup(markup, 'lxml')

        title = soup.title
        if title:
            return title.text

        h1 = soup.h1
        if h1:
            return h1.text

        h2 = soup.h2
        if h2:
            return h2.text

        h3 = soup.h3
        if h2:
            return h3.text

        desc = soup.find('meta', attrs={'name': 'description'})
        if desc:
            return desc['content']

        word = soup.find('meta', attrs={'name': 'keywords'})
        if word:
            return word['content']

        text = soup.text
        if len(text) <= 200:
            return text
        return ''

    def request_callback(self, obj, index, datas):
        try:
            result = obj.result()
        except Exception as e:
            datas[index]['reason'] = str(e.args)
            datas[index]['valid'] = 0
            pass
        else:
            if isinstance(result, tuple):
                resp, text = result

                reason = resp.reason
                status = resp.status
                if resp.status == 400 or resp.status >= 500:
                    title = None
                    banner = None
                    size = 0
                else:
                    headers = resp.headers
                    title = self.get_title(text).strip()
                    size = len(text)
                # f_csv.writerow([index, datas[index]['url'], status, title])
                self.output.statusReport(datas[index]['url'], resp, size)
                # self.output.Last(datas[index]['url'])
                # print([index, datas[index]['url'], status, title])
            else:
                pass

    def gen_new_datas(self, datas, ports):
        new_datas = []
        protocols = ['http://', 'https://']
        for subdomain in datas:
            data = {'subdomain': subdomain}
            for port in ports:
                if port == 80:
                    url = f'http://{subdomain}'
                    data['id'] = None
                    data['url'] = url
                    data['port'] = 80
                    new_datas.append(data)
                    data = dict(data)  # 需要生成一个新的字典对象
                elif port == 443:
                    url = f'https://{subdomain}'
                    data['id'] = None
                    data['url'] = url
                    data['port'] = 443
                    new_datas.append(data)
                    data = dict(data)  # 需要生成一个新的字典对象
                else:
                    for protocol in protocols:
                        url = f'{protocol}{subdomain}:{port}'
                        data['id'] = None
                        data['url'] = url
                        data['port'] = port
                        new_datas.append(data)
                        data = dict(data)  # 需要生成一个新的字典对象
        return new_datas

    def get_ports(self, port):
        ports = set()
        if isinstance(port, set):
            ports = port
        elif isinstance(port, list):
            ports = set(port)
        elif isinstance(port, tuple):
            ports = set(port)
        elif isinstance(port, int):
            if 0 <= port <= 65535:
                ports = {port}
        elif port in {'default', 'small', 'medium', 'large'}:
            ports = config.ports.get(port)
        if not ports:  # 意外情况
            ports = {80}
        return ports

    async def fetch(self, session, url):
        timeout = aiohttp.ClientTimeout(total=None,
                                        connect=None,
                                        sock_read=config.sockread_timeout,
                                        sock_connect=config.sockconn_timeout)
        try:
            async with session.get(url,
                                   ssl=False,
                                   allow_redirects=True,
                                   timeout=timeout,
                                   proxy=None) as resp:
                try:
                    # 先尝试用utf-8解码
                    text = await resp.text(encoding='utf-8', errors='strict')
                except UnicodeError:
                    try:
                        # 再尝试用gb18030解码
                        text = await resp.text(encoding='gb18030',
                                               errors='strict')
                    except UnicodeError:
                        # 最后尝试自动解码
                        text = await resp.text(encoding=None,
                                               errors='ignore')
                return resp, text
        except Exception as e:
            # print(e)
            return e

    def get_limit_conn(self):
        limit_open_conn = config.limit_open_conn
        return limit_open_conn

    def get_connector(self):
        limit_open_conn = self.get_limit_conn()
        return aiohttp.TCPConnector(ttl_dns_cache=300,
                                    ssl=config.verify_ssl,
                                    limit=limit_open_conn,
                                    limit_per_host=config.limit_per_host)

    async def run(self):
        urls = []
        [urls.append(i.strip()) for i in open(self.target).readlines()]
        ports = self.get_ports(self.port)
        new_datas = self.gen_new_datas(urls, ports)
        header = self.get_headers()
        connector = self.get_connector()
        async with ClientSession(connector=connector, headers=header) as session:
            tasks = []
            for i, data in enumerate(new_datas):
                url = data.get('url')
                task = asyncio.ensure_future(self.fetch(session, url))
                task.add_done_callback(functools.partial(self.request_callback,
                                                         index=i,
                                                         datas=new_datas))
                tasks.append(task)
            # 任务列表里有任务不空时才进行解析
            if tasks:
                # 等待所有task完成 错误聚合到结果列表里
                futures = asyncio.as_completed(tasks)
                for i, future in enumerate(futures):
                    self.output.lastPath(new_datas[i]['url'], index=i, length=len(new_datas))
                    await future

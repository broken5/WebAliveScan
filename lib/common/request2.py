import signal
import aiohttp
import asyncio
import functools
from multiprocessing import Manager
from bs4 import BeautifulSoup
import random
import aiomultiprocess as aiomp
import config
from lib.common.output import Output
output = Output()


class Request:
    def __init__(self, target, port):
        self.url_list = self.gen_url_list(target, port)
        self.total = len(self.url_list)
        loop = asyncio.get_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.run())
        # self.output.newLine("OK")

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

    def gen_url_list(self, target, port):
        try:
            # 获取文件内容
            domain_list = open(target, 'r').readlines()

            # 获取端口
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

            # 生成URL
            url_list = []
            protocols = ['http://', 'https://']
            for domain in domain_list:
                domain = domain.strip()
                for port in ports:
                    if port == 80:
                        url = f'http://{domain}'
                        url_list.append(url)
                    elif port == 443:
                        url = f'https://{domain}'
                        url_list.append(url)
                    else:
                        for protocol in protocols:
                            url = f'{protocol}{domain}:{port}'
                            url_list.append(url)
            return url_list
        except FileNotFoundError as e:
            print(e)
            return None

    async def aiohttp_get(self, url):
        # connector = aiohttp.TCPConnector(verify_ssl=config.verify_ssl)
        timeout = aiohttp.ClientTimeout(total=None,
                                        connect=None,
                                        sock_read=config.sockread_timeout,
                                        sock_connect=config.sockconn_timeout)
        try:
            # async with aiohttp.request("GET",
            #                            url,
            #                            timeout=timeout,
            #                            allow_redirects=config.allow_redirects) as response:
            async with aiohttp.ClientSession() as session:
                async with session.get(url=url,
                                       timeout=timeout,
                                       allow_redirects=config.allow_redirects,
                                       ssl=config.verify_ssl) as resp:
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
                    status = resp.status
                    size = len(text)
                    title = self.get_title(text)
                    # result = {'reason': None, 'title': title, 'url': url, 'status': status}
                    # output.statusReport(url, status, size)
                    print(url)
                    return url
        except Exception as e:
            result = {'reason': e, 'url': url}
            return result

    async def aio_fetch(self, pr_queue, url):
        results = await self.aiohttp_get(url)
        pr_queue.put(1)
        print(pr_queue.qsize())
        # output.lastPath(path=url, index=pr_queue.qsize(), length=self.total)
        return results

    def init_worker(self):
        signal.signal(signal.SIGINT, signal.SIG_IGN)

    def save_results(self, results):
        for result in results:
            if result['reason'] is None:
                status = result['status']
                url = result['url']
                title = result['title']
                # print(url, title, status)

    async def run(self):
        # url_list = self.gen_url_list(target, port)
        if self.url_list is not None:
            m = Manager()
            pr_queue = m.Queue()
            wrapped_fetch = functools.partial(self.aio_fetch, pr_queue)
            async with aiomp.Pool(processes=1,
                                  initializer=self.init_worker,
                                  childconcurrency=1024) as pool:
                results = await pool.map(wrapped_fetch, self.url_list)
                # self.save_results(results)
                return


if __name__ == '__main__':
    request = Request('D:\\github\\WebAliveScan\\target.txt', '80')
    # loop = asyncio.get_event_loop()
    # asyncio.set_event_loop(loop)
    # loop.run_until_complete(run('D:\\github\\WebAliveScan\\target.txt', '80'))

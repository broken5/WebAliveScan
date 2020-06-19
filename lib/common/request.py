from gevent import monkey, pool; monkey.patch_all()
from lib.utils.FileUtils import *
import config
import chardet
import time
import random
import urllib3
import requests
from bs4 import BeautifulSoup
urllib3.disable_warnings()


class Request:
    def __init__(self, target, port, output, wappalyzer):
        self.output = output
        self.wappalyzer = wappalyzer
        self.url_list = self.gen_url_list(target, port)
        self.total = len(self.url_list)
        self.output.config(config.threads, self.total)
        self.output.target(target)
        self.index = 0
        self.alive_path = config.result_save_path.joinpath('%s_alive_results.csv' % str(time.time()).split('.')[0])
        self.brute_path = config.result_save_path.joinpath('%s_brute_results.csv' % str(time.time()).split('.')[0])
        self.alive_result_list = []
        self.main()

    def gen_url_by_port(self, domain, port):
        protocols = ['http://', 'https://']
        if port == 80:
            url = f'http://{domain}'
            return url
        elif port == 443:
            url = f'https://{domain}'
            return url
        else:
            url = []
            for protocol in protocols:
                url.append(f'{protocol}{domain}:{port}')
            return url

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
            for domain in domain_list:
                domain = domain.strip()
                if ':' in domain:
                    domain, port = domain.split(':')
                    url = self.gen_url_by_port(domain, int(port))
                    if isinstance(url, list):
                        url_list = url_list + url
                    else:
                        url_list.append(url)
                else:
                    for port in ports:
                        url = self.gen_url_by_port(domain, int(port))
                        if isinstance(url, list):
                            url_list += url
                        else:
                            url_list.append(url)
                    
            return url_list
        except FileNotFoundError as e:
            self.output.debug(e)
            exit()

    def request(self, url):
        try:
            r = requests.get(url, timeout=config.timeout, headers=self.get_headers(), verify=config.verify_ssl,
                             cookies=self.get_cookies(),
                             allow_redirects=config.allow_redirects)
            url_info = self.analysis_response(url, r)
            if url_info:
                self.output.statusReport(url_info)
            else:
                raise Exception
            self.alive_result_list.append(url_info)
            return r,
        except Exception as e:
            return e
        finally:
            self.index = self.index + 1
            self.output.lastPath(url, self.index, self.total)

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

    def get_cookies(self):
        cookies = {'rememberMe': 'test'}
        return cookies

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

    def analysis_response(self, url, response):
        if response.status_code in config.ignore_status_code:
            return None
        response_content = response.content
        html = response_content.decode(encoding=chardet.detect(response_content)['encoding'])
        title = self.get_title(html).strip().replace('\r', '').replace('\n', '')
        status = response.status_code
        size = FileUtils.sizeHuman(len(response.text)).strip()

        soup = BeautifulSoup(html, "html.parser")
        scripts = [script['src'] for script in soup.findAll('script', src=True)]
        meta = {
            meta['name'].lower():
                meta['content'] for meta in soup.findAll(
                'meta', attrs=dict(name=True, content=True))
        }
        detected_apps = self.wappalyzer.analyze(response.url, html, response.headers, scripts, meta)
        application = detected_apps.get('Application') if detected_apps.get('Application') else []
        server = detected_apps.get('Server') if detected_apps.get('Server') else []
        language = detected_apps.get('Language') if detected_apps.get('Language') else []
        frameworks = detected_apps.get('Frameworks') if detected_apps.get('Frameworks') else []
        system = detected_apps.get('System') if detected_apps.get('System') else []
        return {'url': url, 'title': title, 'status': status, 'size': size, 'application': application, 'server': server, 'language': language, 'frameworks': frameworks, 'system': system}

    def main(self):
        gevent_pool = pool.Pool(config.threads)
        while self.url_list:
            tasks = [gevent_pool.spawn(self.request, self.url_list.pop())
                     for i in range(len(self.url_list[:config.threads*10]))]
            for task in tasks:
                task.join()
            del tasks


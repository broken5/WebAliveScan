import random
import requests
import functools
import urllib3
import chardet
import tqdm
from concurrent.futures import ThreadPoolExecutor
import config
from bs4 import BeautifulSoup
import csv
import fire

urllib3.disable_warnings()


def fetch(url):
    try:
        r = requests.get(url, timeout=3, headers=get_headers(), verify=False)
        text = r.content.decode(encoding=chardet.detect(r.content)['encoding'])
        return r, text
    except Exception as e:
        return e


def get_headers():
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


def get_title(markup):
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


def request_callback(obj, index, datas, tqdm_tmp):
    tqdm_tmp.update()
    tqdm_tmp.set_description('Processing Url : %s' % datas[index]['url'])
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
            status = resp.status_code
            if resp.status_code == 400 or resp.status_code >= 500:
                title = None
                banner = None
            else:
                headers = resp.headers
                banner = str({'Server': headers.get('Server'),
                              'Via': headers.get('Via'),
                              'X-Powered-By': headers.get('X-Powered-By')})
                banner = banner[1:-1]
                title = get_title(text).strip()
            f_csv.writerow([index, datas[index]['url'], status, title, banner])
        else:
            pass


def gen_new_datas(datas, ports):
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


def get_ports(port):
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


def run(file, port):
    urls = []
    [urls.append(i.strip()) for i in open(file).readlines()]
    ports = get_ports(port)
    new_datas = gen_new_datas(urls, ports)
    tqdm_tmp = tqdm.tqdm(new_datas)
    with ThreadPoolExecutor(300) as pool:
        for i, data in enumerate(new_datas):
            url = data.get('url')
            pool.submit(fetch, url).add_done_callback(
                functools.partial(request_callback, index=i, datas=new_datas, tqdm_tmp=tqdm_tmp))


if __name__ == '__main__':
    f = open('results.csv', 'w', newline='')
    f_csv = csv.writer(f)
    header = ['id', 'url', 'status', 'title', 'banner']
    f_csv.writerow(header)
    fire.Fire(run)



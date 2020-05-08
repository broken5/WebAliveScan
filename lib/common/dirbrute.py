import requests
import urllib3
import rules
from concurrent.futures import ThreadPoolExecutor
from lib.utils.FileUtils import *
from lib.utils.tools import *
urllib3.disable_warnings()


class Dirbrute:
    def __init__(self, target, output, brute_result_list):
        self.target = target
        self.output = output
        self.output.bruteTarget(target)
        self.all_rules = []
        self.brute_result_list = brute_result_list

    def format_url(self, path):
        url = self.target
        if url.endswith('/'):
            url = url.strip('/')
        if not path.startswith('/'):
            path = '/' + path
        return url + path

    def init_rules(self):
        config_file_rules = rules.common_rules.get('config_file')
        shell_scripts_rules = rules.common_rules.get('shell_scripts')
        editor_rules = rules.common_rules.get('editor')
        spring_rules = rules.common_rules.get('spring')
        web_app_rules = rules.common_rules.get('web_app')
        other_rules = rules.common_rules.get('other')
        self.all_rules += config_file_rules
        self.all_rules += shell_scripts_rules
        self.all_rules += editor_rules
        self.all_rules += spring_rules
        self.all_rules += web_app_rules
        self.all_rules += other_rules

    def compare_rule(self, rule, response_status, response_html, response_content_type):
        rule_status = [200, 206, rule.get('status')]
        if rule.get('status') and (response_status not in rule_status):
            return
        if rule.get('tag') and (rule['tag'] not in response_html):
            return
        if rule.get('type_no') and (rule['type_no'] in response_content_type):
            return
        if rule.get('type') and (rule['type'] not in response_content_type):
            return
        return True

    def brute(self, rule):
        user_agent = 'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
        headers = {'User-Agent': user_agent, 'Connection': 'Keep-Alive', 'Range': 'bytes=0-102400'}
        url = self.format_url(rule['path'])
        try:
            r = requests.get(url, headers=headers, verify=False, timeout=3)
        except Exception as e:
            return e
        size = FileUtils.sizeHuman(len(r.text))
        response_status = r.status_code
        response_html = r.text
        response_content_type = r.headers['Content-Type']
        for white_rule in rules.white_rules:
            if self.compare_rule(white_rule, response_status, response_html, response_content_type):
                self.output.statusReport(url, response_status, size)
        if not self.compare_rule(rule, response_status, response_html, response_content_type):
            return
        result = [url, str(response_status), size]
        self.brute_result_list.append(result)
        self.output.statusReport(url, response_status, size, '')
        return [url, rule]

    def run(self):
        self.init_rules()
        with ThreadPoolExecutor(30) as pool:
            for rule in self.all_rules:
                pool.submit(self.brute, rule)

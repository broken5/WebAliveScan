import re
import json
import config
import requests


class Wappalyzer(object):
    """
    Python Wappalyzer driver.
    """

    def __init__(self):
        apps_file = config.realpath.joinpath('apps.json')
        with open(apps_file, 'r') as fd:
            obj = json.load(fd)
        # self.categories = obj['categories']
        self.apps = obj['apps']
        for name, app in self.apps.items():
            self._prepare_app(app)
        self.url = ''
        self.html = ''
        self.headers = ''
        self.scripts = ''
        self.meta = ''

    def _prepare_app(self, app):
        """
        Normalize app data, preparing it for the detection phase.
        """

        # Ensure these keys' values are lists
        for key in ['url', 'html', 'script', 'implies']:
            value = app.get(key)
            if value is None:
                app[key] = []
            else:
                if not isinstance(value, list):
                    app[key] = [value]

        # Ensure these keys exist
        for key in ['headers', 'meta']:
            value = app.get(key)
            if value is None:
                app[key] = {}

        # Ensure the 'meta' key is a dict
        obj = app['meta']
        if not isinstance(obj, dict):
            app['meta'] = {'generator': obj}

        # Ensure keys are lowercase
        for key in ['headers', 'meta']:
            obj = app[key]
            app[key] = {k.lower(): v for k, v in obj.items()}

        # Prepare regular expression patterns
        for key in ['url', 'html', 'script']:
            app[key] = [self._prepare_pattern(pattern) for pattern in app[key]]

        for key in ['headers', 'meta']:
            obj = app[key]
            for name, pattern in obj.items():
                obj[name] = self._prepare_pattern(obj[name])

    def _prepare_pattern(self, pattern):
        """
        Strip out key:value pairs from the pattern and compile the regular
        expression.
        """
        regex, _, rest = pattern.partition('\\;')
        try:
            return re.compile(regex, re.I)
        except re.error as e:
            # regex that never matches:
            # http://stackoverflow.com/a/1845097/413622
            return re.compile(r'(?!x)x')

    def _has_app(self, app):
        """
        Determine whether the web page matches the app signature.
        """
        # Search the easiest things first and save the full-text search of the
        # HTML for last

        for regex in app['url']:
            if regex.search(self.url):
                return True

        for name, regex in app['headers'].items():
            if name in self.headers:
                content = self.headers[name]
                if regex.search(content):
                    return True

        for regex in app['script']:
            for script in self.scripts:
                if regex.search(script):
                    return True

        for name, regex in app['meta'].items():
            if name in self.meta:
                content = self.meta[name]
                if regex.search(content):
                    return True

        for regex in app['html']:
            if regex.search(self.html):
                return True

    def _get_implied_apps(self, detected_apps):
        """
        Get the set of apps implied by `detected_apps`.
        """

        def __get_implied_apps(apps):
            _implied_apps = set()
            for app in apps:
                if 'implies' in self.apps[app]:
                    _implied_apps.update(set(self.apps[app]['implies']))
            return _implied_apps

        implied_apps = __get_implied_apps(detected_apps)
        all_implied_apps = set()

        # Descend recursively until we've found all implied apps
        while not all_implied_apps.issuperset(implied_apps):
            all_implied_apps.update(implied_apps)
            implied_apps = __get_implied_apps(all_implied_apps)

        return all_implied_apps

    def analyze(self, url, html, headers, scripts, meta):
        """
        Return a list of applications that can be detected on the web page.
        """
        detected_apps = {}
        self.url = url
        self.html = html
        self.headers = headers
        self.scripts = scripts
        self.meta = meta
        for app_name, app in self.apps.items():
            # print(app)
            if self._has_app(app):
                if app['cats'] not in detected_apps:
                    detected_apps[app['cats']] = [app_name]
                else:
                    detected_apps[app['cats']].append(app_name)
        return detected_apps


if __name__ == '__main__':
    r = requests.get('https://www.discuz.net/', verify=False)
    w = Wappalyzer()
    data = w.analyze(r.url, r.text, r.headers, 'test', 'test')
    print(data)

import platform
import sys
import threading
import time
import urllib.parse
from lib.utils.TerminalSize import get_terminal_size
from thirdparty.colorama import *

if platform.system() == 'Windows':
    from thirdparty.colorama.win32 import *


class Output(object):
    def __init__(self):
        init()
        self.lastLength = 0
        self.lastOutput = ''
        self.lastInLine = False
        self.mutex = threading.Lock()
        self.blacklists = {}
        self.mutexCheckedPaths = threading.Lock()
        self.basePath = None
        self.errors = 0

    def inLine(self, string):
        self.erase()
        sys.stdout.write(string)
        sys.stdout.flush()
        self.lastInLine = True

    def erase(self):
        if platform.system() == 'Windows':
            csbi = GetConsoleScreenBufferInfo()
            line = "\b" * int(csbi.dwCursorPosition.X)
            sys.stdout.write(line)
            width = csbi.dwCursorPosition.X
            csbi.dwCursorPosition.X = 0
            FillConsoleOutputCharacter(STDOUT, ' ', width, csbi.dwCursorPosition)
            sys.stdout.write(line)
            sys.stdout.flush()

        else:
            sys.stdout.write('\033[1K')
            sys.stdout.write('\033[0G')

    def newLine(self, string):
        if self.lastInLine == True:
            self.erase()

        if platform.system() == 'Windows':
            sys.stdout.write(string)
            sys.stdout.flush()
            sys.stdout.write('\n')
            sys.stdout.flush()

        else:
            sys.stdout.write(string + '\n')

        sys.stdout.flush()
        self.lastInLine = False
        sys.stdout.flush()

    def statusReport(self, url_info):
        url = url_info['url']
        status = url_info['status']
        size = url_info['size']
        title = url_info['title']
        application = ','.join(url_info['application'])
        server = ','.join(url_info['server'])
        frameworks = ','.join(url_info['frameworks'])
        language = ','.join(url_info['language'])
        system = ','.join(url_info['system'])
        with self.mutex:
            url = f'{Style.BRIGHT}URL{Style.RESET_ALL}[{Fore.CYAN}{url}{Style.RESET_ALL}]'
            status = f'{Style.BRIGHT}Status{Style.RESET_ALL}[{status}]'
            size = f'{Style.BRIGHT}Size{Style.RESET_ALL}[{Fore.YELLOW}{size}{Style.RESET_ALL}]'
            title = f' {Style.BRIGHT}Title{Style.RESET_ALL}[{Fore.RED}{title}{Style.RESET_ALL}]' if title else ''
            application = f' {Style.BRIGHT}Application{Style.RESET_ALL}[{Fore.GREEN}{application}{Style.RESET_ALL}]' if application else ''
            server = f' {Style.BRIGHT}Server{Style.RESET_ALL}[{Fore.GREEN}{server}{Style.RESET_ALL}]' if server else ''
            frameworks = f' {Style.BRIGHT}Frameworks{Style.RESET_ALL}[{Fore.GREEN}{frameworks}{Style.RESET_ALL}]' if frameworks else ''
            language = f' {Style.BRIGHT}Language{Style.RESET_ALL}[{Fore.GREEN}{language}{Style.RESET_ALL}]' if language else ''
            system = f' {Style.BRIGHT}System{Style.RESET_ALL}[{Fore.GREEN}{system}{Style.RESET_ALL}]' if system else ''
            message = f'[{time.strftime("%H:%M:%S")}] {url} {status} {size}{title}{application}{server}{frameworks}{language}{system}'
            self.newLine(message)

    def lastPath(self, path, index, length):
        with self.mutex:
            percentage = lambda x, y: float(x) / float(y) * 100

            x, y = get_terminal_size()
            message = '{index}/{length} - '.format(index=index, length=length)
            if self.errors > 0:
                message = Style.BRIGHT + Fore.RED
                message += 'Errors: {0}'.format(self.errors)
                message += Style.RESET_ALL
                message += ' - '

            message += 'Last request to: {0}'.format(path)

            if len(message) > x:
                message = message[:x]

            self.inLine(message)

    def addConnectionError(self):
        self.errors += 1

    def error(self, reason):
        with self.mutex:
            stripped = reason.strip()
            start = reason.find(stripped[0])
            end = reason.find(stripped[-1]) + 1
            message = reason[0:start]
            message += Style.BRIGHT + Fore.WHITE + Back.RED
            message += reason[start:end]
            message += Style.RESET_ALL
            message += reason[end:]
            self.newLine(message)

    def warning(self, reason):
        message = Style.BRIGHT + Fore.YELLOW + reason + Style.RESET_ALL
        self.newLine(message)

    def header(self, text):
        message = Style.BRIGHT + Fore.MAGENTA + text + Style.RESET_ALL
        self.newLine(message)

    def config(self, threads, list_size):
        separator = Fore.MAGENTA + ' | ' + Fore.YELLOW
        config = Style.BRIGHT + Fore.YELLOW
        config += 'Threads: {0}'.format(Fore.CYAN + str(threads) + Fore.YELLOW)
        config += separator
        config += 'Number of requests: {0}'.format(Fore.CYAN + str(list_size) + Fore.YELLOW)

        config += Style.RESET_ALL

        self.newLine(config)

    def target(self, target):
        config = Style.BRIGHT + Fore.YELLOW
        config += '\nTarget: {0}\n'.format(Fore.CYAN + target + Fore.YELLOW)
        config += Style.RESET_ALL

        self.newLine(config)

    def bruteTarget(self, target):
        config = Style.BRIGHT + Fore.YELLOW
        config += '\nDirBrute Target: {0}\n'.format(Fore.CYAN + target + Fore.YELLOW)
        config += Style.RESET_ALL

        self.newLine(config)

    def resultOutput(self, _str):
        config = Style.BRIGHT + Fore.YELLOW
        config += '\n{0}\n'.format(Fore.GREEN + _str + Style.RESET_ALL)
        config += Style.RESET_ALL

        self.newLine(config)

    def debug(self, info):
        line = "[{0}] - {1}".format(time.strftime('%H:%M:%S'), info)
        self.newLine(line)

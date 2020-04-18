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

    def statusReport(self, path, status, size, title):
        with self.mutex:
            if self.basePath is None:
                showPath = urllib.parse.urljoin("/", path)
            else:
                showPath = urllib.parse.urljoin("/", self.basePath)
                showPath = urllib.parse.urljoin(showPath, path)
            if title:
                message = '[{0}] {1} - {2} - {3} - {4}'.format(
                    time.strftime('%H:%M:%S'),
                    status,
                    size.rjust(6, ' '),
                    showPath,
                    title
                )
            else:
                message = '[{0}] {1} - {2} - {3}'.format(
                    time.strftime('%H:%M:%S'),
                    status,
                    size.rjust(6, ' '),
                    showPath
                )
            message = Fore.GREEN + message + Style.RESET_ALL

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

    def debug(self, info):
        line = "[{0}] - {1}".format(time.strftime('%H:%M:%S'), info)
        self.newLine(line)

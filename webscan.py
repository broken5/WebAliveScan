from lib.common.request import Request
from lib.common.output import Output
import fire


class Program(object):
    def __init__(self, target, port):
        self.output = Output()
        self.request = Request(target, port, self.output)


def run(target, port):
    main = Program(target, port)


if __name__ == '__main__':
    fire.Fire(run)

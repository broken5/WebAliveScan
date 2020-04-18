from lib.common.request import Request
from lib.common.output import Output
from lib.common.dirbrute import Dirbrute
from lib.utils.tools import *
import fire


class Program(object):
    def __init__(self, target, port, brute):
        output = Output()
        request = Request(target, port, output)
        if brute:
            output.newLine('')
            save_result(request.brute_path, ['url', 'status', 'size'], None)
            for url in request.alive_web:
                dirbrute = Dirbrute(url, output, request.brute_path)
                dirbrute.run()


def run(target, port, brute=False):
    main = Program(target, port, brute)


if __name__ == '__main__':
    fire.Fire(run)

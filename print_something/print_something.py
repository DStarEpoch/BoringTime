# -*- coding: utf-8 -*-
import numpy as np
from async_util import Async
import os


class Buffer(object):

    def __init__(self, fn: str):
        with open(fn, 'r') as f:
            self.all_lines = f.readlines()

    @Async
    def Print(self):
        while True:
            wait_t = np.random.exponential(0.1)
            start = np.random.randint(0, len(self.all_lines)-1)
            line_len = abs(int(np.random.normal(20, 5)))
            if start + line_len > len(self.all_lines):
                for ll in self.all_lines[start:]:
                    print(ll)
            else:
                for ll in self.all_lines[start:start+line_len]:
                    print(ll)
            yield wait_t


if __name__ == '__main__':
    os.chdir(os.path.join(os.path.split(os.path.realpath(__file__))[0]))
    B = Buffer('./out2.log')
    B.Print()

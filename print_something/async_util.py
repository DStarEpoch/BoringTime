# -*- coding: utf-8 -*-
"""
The simplest async tool
"""
import time
from threading import Timer
import inspect


def Async(func):
    return AsyncDescriptor(func)


class AsyncDescriptor(object):

    def __init__(self, func):
        # generate method descriptor
        self.func = func

    def __repr__(self):
        return 'AsyncDescriptor<%s>' % self.func

    def __get__(self, obj, cls):
        # when called function -> instance method
        if obj is None:
            return self
        method = self.func.__get__(obj, cls)
        return AsyncDescriptor(method)

    def __call__(self, *args, **kwargs):
        if inspect.ismethod(self.func):
            entity = self.func.__self__
        else:
            entity = None

        generator = self.func(*args, **kwargs)
        ret = AsyncFuncNode(generator, entity)

        ret._startNext()
        return ret


class AsyncFuncNode(object):

    def __init__(self, generator, entity):
        self.generator = generator
        self.entity = entity

        self.dead = False
        self.running = False

        self.root = self

        self.inner_timer = None
        self.t_start, self.t_wait = None, None

    def __str__(self):
        if self.dead:
            return 'AsyncFuncNode(Dead)'
        else:
            return 'AsyncFuncNode{generator: %s}' % self.generator

    def _release(self):
        self.__dict__.clear()
        self.dead = True

    ############run frame#################
    def _startNext(self):
        self.inner_timer = None
        root = self.root
        root._next()

    def _next(self):
        self.running = True

        try:
            cur_frame_res = next(self.generator)
        except StopIteration:
            self._release()
            return

        if type(cur_frame_res) in (int, float):
            t_wait = cur_frame_res
            if t_wait < 0:
                raise Exception('wait time must be non-negative: %s, %s' %
                                (t_wait, self.generator))
            elif t_wait == 0:
                t_wait += 1e-3

            self.t_wait = t_wait
            self.t_start = time.time()
            self._addTimer(self.t_wait)
        else:
            raise Exception('unsupported return type.')

        self.running = False
        return

    def _addTimer(self, delay):
        ret = Timer(delay, self._startNext)
        ret.start()
        self.inner_timer = ret


if __name__ == '__main__':
    class A(object):
        @Async
        def foo(self):
            c = 0
            for i in range(10):
                print("foo ", i, end='')
                c += 1.5
                yield 1.5
                print(" cumtime: ", c)
    a = A()
    a.foo()

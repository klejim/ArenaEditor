# -*- coding: UTF-8 -*-
"""
Classes génériques implémentant la gestion (annulation/rétablissement) d'actions
"""
from abc import ABCMeta, abstractmethod
from profiling import benchmark


class Operation(metaclass=ABCMeta):
    @abstractmethod
    def do():
        pass

    @abstractmethod
    def undo():
        pass


class StartPaintGroup(Operation):
    def undo(self): pass

    def do(self): pass

    def __str__(self):
        return "\nSTART GROUP : "

    def __repr__(self):
        return self.__str__()


class EndPaintGroup(Operation):
    def undo(self): pass

    def do(self): pass

    def __str__(self):
        return "END GROUP :\n"

    def __repr__(self):
        return self.__str__()


class Handler:
    def __init__(self, max=200):
        self.done = []
        self.undone = []
        self.max_op = max

    def nothingToDo(self):
        return not self.undone

    def nothingToUndo(self):
        return not self.done

    def push(self, op):
        self.done.append(op)
        while len(self.done) > self.max_op:
            self.done.pop(0)

    @benchmark
    def undo(self, n=1):
        if len(self.done) >= n:
            n = n if n < self.max_op else self.max_op
            for i in range(n):
                op = self.done.pop()
                op.undo()
                self.undone.append(op)
            while len(self.undone) > self.max_op:
                self.undone.pop(0)

    @benchmark
    def undoGroup(self):
        if self.done:
            op = None
            n = 0
            while self.done and not isinstance(op, EndPaintGroup):
                op = self.done.pop()
            self.push(op)
            # op is a EndPaintGroup
            for op in reversed(self.done):
                n += 1
                if isinstance(op, StartPaintGroup):
                    break
            self.undo(n)

    def redoGroup(self):
        if self.undone:
            op = None
            n = 0
            while self.undone and not isinstance(op, StartPaintGroup):
                op = self.undone.pop()
            self.push(op)
            # op is a StartPaintGroup
            for op in reversed(self.undone):
                n += 1
                if isinstance(op, EndPaintGroup):
                    break
            self.redo(n)

    def redo(self, n=1):
        if len(self.undone) >= n:
            n = n if n < self.max_op else self.max_op
            for i in range(n):
                op = self.undone.pop()
                op.do()
                self.done.append(op)
            while (len(self.done) > self.max_op):
                self.done.pop(0)

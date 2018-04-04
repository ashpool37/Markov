import argparse
import string
import re
from collections import defaultdict

argParser = argparse.ArgumentParser(
    description="Train a Markov model based on text files.")
#argParser.add_argument()


class Tree:
    @staticmethod
    def _factory():
        return defaultdict(Tree._factory)

    def __init__(self):
        self._tree = Tree._factory()

    def inc_ctx(self, context):
        subtree = self._tree
        for node in context[:-1]:
            subtree = subtree[node]
        fkey = context[-1]
        if not subtree.get(fkey):
            subtree[fkey] = 1
        else:
            subtree[fkey] += 1


class MarkovModel:
    def __init__(self, ctxLength):
        self.chains = Tree()
        self.ctxLength = ctxLength

    def train(self, ifs):
        context = []
        for line in ifs:
            words = line.strip().split()
            words = [w.strip(string.punctuation) for w in words]
            for word in words:
                context.append(word)
                if len(context) < self.ctxLength + 1:
                    continue
                self.chains.inc_ctx(context)
                del context[0]


mm = MarkovModel(2)
arg_ifs = open("sonnets.txt", 'r')
mm.train(arg_ifs)
pass

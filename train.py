import argparse
import string
import json
from collections import defaultdict

argParser = argparse.ArgumentParser(
    description="Train a Markov model based on text files.")


# argParser.add_argument()


class MarkovModel:
    class Tree:
        @staticmethod
        def _factory():
            return defaultdict(MarkovModel.Tree._factory)

        def __init__(self):
            self._tree = MarkovModel.Tree._factory()

        def inc_ctx(self, context):
            subtree = self._tree
            for node in context[:-1]:
                subtree = subtree[node]
            fkey = context[-1]
            if not subtree.get(fkey):
                subtree[fkey] = 1
            else:
                subtree[fkey] += 1

        def traverse(self, depth, tree=None):
            if not tree:
                tree = self._tree
            if depth > 0:
                for key, subtree in tree.items():
                    self.traverse(depth - 1, subtree)
                return
            # else we have leaves
            leafsum = 0
            for key, leaf in tree.items():
                leafsum += leaf
            for key in tree.keys():
                tree[key] = "%.4f" % (tree[key] / leafsum)

    def __init__(self, ctx_length):
        self.chains = MarkovModel.Tree()
        self.ctxLength = ctx_length

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

    def finalize(self):
        self.chains.traverse(self.ctxLength)

    def dump(self, ofs):
        json.dump(self.chains._tree, ofs)


mm = MarkovModel(2)
arg_ifs = open("sonnets.txt", 'r')
arg_ofs = open("model.json", 'w')
mm.train(arg_ifs)
mm.finalize()
mm.dump(arg_ofs)
pass

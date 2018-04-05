import string
import json
from collections import defaultdict


class Model:
    class Tree:
        @staticmethod
        def _factory():
            return defaultdict(Model.Tree._factory)

        def __init__(self):
            self._tree = Model.Tree._factory()

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

    def __init__(self, ctx_length, lower=True):
        self.chains = Model.Tree()
        self.ctxLength = ctx_length
        self.lower = lower

    def train(self, ifs):
        context = []
        for line in ifs:
            if self.lower:
                line = line.lower()
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
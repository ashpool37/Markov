import string
import json
import random
from collections import defaultdict


class Model:
    class Tree:
        @staticmethod
        def _factory():
            return defaultdict(Model.Tree._factory)

        def __init__(self):
            self.tree = Model.Tree._factory()

        def inc_ctx(self, context):
            subtree = self.tree
            for node in context[:-1]:
                subtree = subtree[node]
            fkey = context[-1]
            if not subtree.get(fkey):
                subtree[fkey] = 1
            else:
                subtree[fkey] += 1

        def get_next(self, context):
            subtree = self.tree
            for node in context:
                subtree = subtree[node]
                if subtree is None:
                    return None
            return subtree

        def random_ctx(self, length):
            subtree = self.tree
            ctx = []
            for k in range(length):
                next_word = random.choices(list(subtree.keys()))[0]
                ctx.append(next_word)
                subtree = subtree[next_word]
            return ctx

        # def traverse(self, depth, tree=None):
        #     if not tree:
        #         tree = self.tree
        #     if depth > 0:
        #         for key, subtree in tree.items():
        #             self.traverse(depth - 1, subtree)
        #         return
        #     # else we have leaves
        #     leafsum = 0
        #     for key, leaf in tree.items():
        #         leafsum += leaf
        #     for key in tree.keys():
        #         tree[key] = round(tree[key] / leafsum, 5)

    def __init__(self, ctx_length, lower=True):
        self.chains = Model.Tree()
        self.ctxLength = ctx_length
        self.lower = lower

    @classmethod
    def load(cls, ifs):
        inp = json.load(ifs)
        ctx_length = inp['context']
        mm = cls(ctx_length)
        mm.chains.tree = inp['tree']
        return mm

    @classmethod
    def empty(cls, ctx_length, lower=True):
        return cls(ctx_length, lower)

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

    # def finalize(self):
    #     self.chains.traverse(self.ctxLength)

    def dump(self, ofs):
        model_dump = {'context': self.ctxLength,
                      'tree': self.chains.tree}
        json.dump(model_dump, ofs)

    def generate(self, ofs, length, start_ctx=None, reseed_random=True):
        if not start_ctx:
            start_ctx = self.chains.random_ctx(self.ctxLength)
        ctx = start_ctx
        for word in ctx:
            ofs.write("{} ".format(word))
        for wcount in range(length):
            next_candidates = self.chains.get_next(ctx)
            if not next_candidates:
                if not reseed_random:
                    ctx = start_ctx
                    next_candidates = self.chains.get_next(ctx)
                if not next_candidates or reseed_random:
                    while not next_candidates:
                        ctx = self.chains.random_ctx(self.ctxLength)
                        next_candidates = self.chains.get_next(ctx)
                for word in ctx:
                    ofs.write("{} ".format(word))

            words = list(next_candidates.keys())
            weights = list(next_candidates.values())
            next_word = random.choices(words, weights=weights)[0]
            ofs.write("{} ".format(next_word))
            del ctx[0]
            ctx.append(next_word)

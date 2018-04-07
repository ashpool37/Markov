"""
A module for training Markov models, representing them with JSON and using them
to generate texts.
"""

import string
import json
import random
from collections import defaultdict


class Model:
    """
    Representation of a Markov model characterized by an integer context length
    C >= 1. Training a model on a text means counting the number of occurencies
    of each contiguous (C+1)-word string found in text. Generating text using
    a model means printing a given number of words, where for each C contiguous
    words (a context) the range of words from which to choose the next one and
    their probabilities of appearing are the same as in the original text used
    to train the model, yet the choice is randomized. For the sake of memory and
    disk space preservation, as well as speeding-up training and generating
    routines, a tree is used to store contexts and their follow-up probabilites,
    which ensures O(C) context search time.
    """
    class ChainTree:
        """
        Wrapper around the recursive tree data structure used to store
        contexts and following words probabilities.
        """
        @staticmethod
        def factory(*args, **kwargs) -> defaultdict:
            """
            Tree factory. Returns a defaultdict whose default values are also
            defaultdicts, optionally populating it with *args and **kwargs the
            same way as if they would be passed to dict().
            """
            return defaultdict(Model.ChainTree.factory, *args, **kwargs)

        def __init__(self, ctx_length: int):
            self.tree = Model.ChainTree.factory()
            self.ctx_length = ctx_length

        def inc_count(self, context: list, follower: str):
            subtree = self.tree
            for node in context:
                subtree = subtree[node]
            if not subtree.get(follower):
                subtree[follower] = 1
            else:
                subtree[follower] += 1

        def get_next(self, context: list) -> defaultdict:
            subtree = self.tree
            for node in context:
                subtree = subtree[node]
                if not subtree:
                    break
            return subtree

        def random_ctx(self):
            subtree = self.tree
            ctx = []
            for k in range(self.ctx_length):
                next_word = random.choices(list(subtree.keys()))[0]
                ctx.append(next_word)
                subtree = subtree[next_word]
            return ctx

    def __init__(self, ctx_length, lower=True):
        self.chains = Model.ChainTree(ctx_length)
        self.lower = lower

    @classmethod
    def load(cls, ifs):
        inp = json.load(ifs, object_pairs_hook=Model.ChainTree.factory)
        ctx_length = inp['context']
        markov_model = cls(ctx_length)
        markov_model.chains.tree = inp['tree']
        return markov_model

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
                if len(context) == self.chains.ctx_length:
                    self.chains.inc_count(context, word)
                    del context[0]
                context.append(word)

    def dump(self, ofs):
        model_dump = {'context': self.chains.ctx_length,
                      'tree': self.chains.tree}
        json.dump(model_dump, ofs)

    def generate(self, ofs, length, start_ctx=None, reseed_random=True):
        if not start_ctx:
            start_ctx = self.chains.random_ctx()
        ctx = start_ctx
        for word in ctx:
            ofs.write(word + ' ')
        for wcount in range(length):
            next_candidates = self.chains.get_next(ctx)
            if not next_candidates:
                if not reseed_random:
                    ctx = start_ctx
                    next_candidates = self.chains.get_next(ctx)
                if not next_candidates or reseed_random:
                    while not next_candidates:
                        ctx = self.chains.random_ctx()
                        next_candidates = self.chains.get_next(ctx)
                for word in ctx:
                    ofs.write(word + ' ')

            words = list(next_candidates.keys())
            weights = list(next_candidates.values())
            next_word = random.choices(words, weights=weights)[0]
            ofs.write(next_word + ' ')
            del ctx[0]
            ctx.append(next_word)

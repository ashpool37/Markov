"""
A module for training Markov models, representing them with JSON and using them
to generate texts.
"""

import string
import json
import typing
import random
from collections import defaultdict
from collections import deque
from .io import WordWriter


class Model:
    """
    Representation of a Markov model characterized by an integer context length
    C >= 1. Training a model on a text means counting the number of occurencies
    of each contiguous (C+1)-word string found in text. Generating text using
    a model means printing a given number of words, where for each C contiguous
    words (a context) the range of words from which to choose the next one and
    their probabilities of appearing are the same as in the original text used
    to train the model, yet the choice is randomized. For the sake of memory
    and disk space preservation, as well as speeding-up training and generating
    routines, a tree is used to store contexts and their follow-up
    probabilites, which ensures O(C) context search time.
    """

    class ChainTree:
        """
        Wrapper around the recursive tree data structure used to store
        contexts and following words probabilities.
        An example subtree for C = 2 would be:

        [root]
        |--"lorem"
        |  `--"ipsum"
        |     |--"dolor" : 2   < "lorem ipsum dolor" appeared 2 times
        |     `--"amet" : 5    < "lorem ipsum amet" appeared 5 times
        `--"ipsum"
           `--"dolor"
              `--"sit" : 6     < "ipsum dolor sit" appeared 6 times

        "lorem ipsum" and "ipsum dolor" are contexts in the example above.
        """

        @staticmethod
        def factory(*args, **kwargs) -> defaultdict:
            """
            Tree factory. Returns a defaultdict whose default values are also
            defaultdicts, optionally populating it with *args and **kwargs the
            same way as if they would be passed to dict().
            """
            return defaultdict(Model.ChainTree.factory, *args, **kwargs)

        def __init__(self, ctx_length: int, tree: defaultdict = None):
            """:param ctx_length: context length of the tree """
            self.tree = tree or Model.ChainTree.factory()
            self.ctx_length = ctx_length

        def inc_count(self, context: list, follower: str):
            """
            Increase the counter for the given following word in the given
            context. If such a word has never seen before in this context,
            initialize the counter with 1.
            :param context: a list of strings representing context
            :param follower: a string with the word which was found following
            this context
            """
            subtree = self.tree
            for node in context:
                subtree = subtree[node]
            if not subtree.get(follower):
                subtree[follower] = 1
            else:
                subtree[follower] += 1

        def get_next(self, context: list) -> defaultdict:
            """
            :param context: a list of strings representing context
            :return: a subtree (defaultdict) containing words that may go after
            this context and their counts.
            """
            subtree = self.tree
            for node in context:
                subtree = subtree[node]
                if not subtree:
                    break
            return subtree

        def random_ctx(self) -> list:
            """
            :return: a list of strings representing a randomly chosen context
            from the tree
            """
            subtree = self.tree
            ctx = []
            for k in range(self.ctx_length):
                next_word = random.choices(list(subtree.keys()))[0]
                ctx.append(next_word)
                subtree = subtree[next_word]
            return ctx

    def __init__(self, ctx_length: int, lower: bool = True,
                 tree: defaultdict = None):
        """
        :param ctx_length: context length of the model
        :param lower: if True, the words will be converted to lower case when
        training
        :param tree: a tree to initialize the model with
        """
        self.chains = Model.ChainTree(ctx_length, tree)
        self.lower = lower

    @classmethod
    def load(cls, ifs: typing.TextIO):
        """
        Build a model using a json-serialized model from file.
        :param ifs: file object to read json from
        :return: a built Markov model
        """
        inp = json.load(ifs, object_pairs_hook=Model.ChainTree.factory)
        ctx_length = inp['context']
        markov_model = cls(ctx_length, tree=inp['tree'])
        return markov_model

    @classmethod
    def empty(cls, ctx_length: int, lower: bool = True):
        """
        Build an empty model
        :param ctx_length: context length of the model
        :param lower: if True, the words will be converted to lower case when
        training
        :return: an empty Markov model
        """
        return cls(ctx_length, lower)

    def train(self, ifs: typing.TextIO):
        """
        Train a model using a text file
        :param ifs: file object to read text from
        """
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

    def dump(self, ofs: typing.TextIO):
        """
        Write a json serialization of a model to a file object
        :param ofs: file object to output json to
        """
        model_dump = {'context': self.chains.ctx_length,
                      'tree': self.chains.tree}
        json.dump(model_dump, ofs)

    def generate(self, ofs: typing.TextIO, length: int, width: int,
                 start_ctx: list = None, reseed_random: bool = True):
        """
        Generate a text of the given length and write it to a file object.
        This procedure can sometimes try to search for non-existent context in
        the tree, depending on the text used to train the model. In that case,
        reseeding is done using a random context if reseed_random == False, or
        the start_ctx otherwise (which is also chosen randomly if omitted).
        :param ofs: file object to output text to
        :param length: number of words to output
        :param width: maximum characters per line
        :param start_ctx: initial context state, randomly chosen if omitted
        :param reseed_random: use randomly chosen context for reseeding if
        true, use start_ctx each time otherwise.
        """
        writer = WordWriter(ofs, width)

        if not start_ctx:
            start_ctx = self.chains.random_ctx()
        ctx = start_ctx
        ctx_buffer = deque()
        ctx_buffer.extend(ctx)
        for wcount in range(length):
            if ctx_buffer:
                writer.write(ctx_buffer.popleft())
                continue

            next_candidates = self.chains.get_next(ctx)
            if not next_candidates:
                if not reseed_random:
                    ctx = start_ctx
                    next_candidates = self.chains.get_next(ctx)
                if not next_candidates or reseed_random:
                    while not next_candidates:
                        ctx = self.chains.random_ctx()
                        next_candidates = self.chains.get_next(ctx)
                ctx_buffer.extend(ctx)

            words = list(next_candidates.keys())
            weights = list(next_candidates.values())
            next_word = random.choices(words, weights=weights)[0]
            writer.write(next_word)
            del ctx[0]
            ctx.append(next_word)

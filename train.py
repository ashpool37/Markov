"""
Script to train a Markov model to be later used by generate.py for generating
texts.
"""

import argparse
import sys
import os
from Markov import Model


def main():
    aparse = argparse.ArgumentParser(
        description="Train a Markov model based on text files.",
        add_help=False)
    aparse.add_argument('--ctx', type=int, default=1,
                        help="Length of context (number of words). 1 by "
                             "default.")
    aparse.add_argument('--input', dest='ifs', default=sys.stdin,
                        type=argparse.FileType('r', encoding='utf8'),
                        help="Path to the input file. If both this and "
                             "--input-dir are ommitted, read from stdin.")
    aparse.add_argument('--input-dir', default=None,
                        help="Path to the input directory with .txt files.")
    aparse.add_argument('--model', dest='ofs',
                        type=argparse.FileType('w', encoding='utf8'),
                        default=sys.stdout,
                        help="Path to the output model file. "
                             "Print to stdout by default")
    aparse.add_argument('--lc', action="store_true",
                        help="Convert input texts to lower case")
    aparse.add_argument('--help', action="help",
                        help="Display this help message and exit")

    args = aparse.parse_args()

    if args.ctx < 1:
        print("Please specify a positive --ctx.")
        exit(1)

    markov_model = Model.empty(ctx_length=args.ctx, lower=args.lc)
    if args.input_dir is not None:
        for file in os.listdir(args.input_dir):
            if file.endswith(".txt"):
                fpath = os.path.join(args.input_dir, file)
                with open(fpath, 'r', encoding="utf8") as ifs:
                    markov_model.train(ifs)
    else:
        markov_model.train(args.ifs)
        args.ifs.close()

    markov_model.dump(args.ofs)
    args.ofs.close()


if __name__ == "__main__":
    main()

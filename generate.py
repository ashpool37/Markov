"""
Script to generate a text of given length using an existing Markov model
trained by train.py.
"""

import argparse
import sys
from Markov import Model


def main():
    aparse = argparse.ArgumentParser(
        description="Use an existing Markov model to generate new text of "
                    "given length.",
        add_help=False)
    aparse.add_argument('--model', dest='ifs', default=sys.stdin,
                        type=argparse.FileType('r', encoding='utf8'),
                        help="Path to the input file containing a "
                             "json-encoded model generated by train.py. Read "
                             "from stdin by default.")
    aparse.add_argument('--seed', default=None,
                        help="First C space-separated words to seed the "
                             "generator, where C is the model's context "
                             "length. Should be quote-enclosed if C > 1. "
                             "Chosen randomly by default.")
    aparse.add_argument('--length', type=int, required=True,
                        help="Length of the generated text.")
    aparse.add_argument('--output', default=sys.stdout, dest='ofs',
                        type=argparse.FileType('w', encoding='utf8'),
                        help="Path to the output file. Print to stdout by "
                             "default.")
    aparse.add_argument('--width', type=int, default=79,
                        help="Maximum characters per line (excluding newline)."
                             "79 by default.")
    aparse.add_argument('--help', action="help",
                        help="Display this help message and exit")

    args = aparse.parse_args()

    markov_model = Model.load(args.ifs)
    args.ifs.close()

    if args.length < markov_model.chains.ctx_length + 1:
        print("Please specify a length greater than model's context length.")
        exit(1)

    if args.width < 2:
        print("Text must be at least 2 characters wide, newline excluded.")
        exit(1)

    if args.seed is not None:
        args.seed = args.seed.strip().split()
        if len(args.seed) != markov_model.chains.ctx_length:
            print("Please specify exactly C words in the seed, where C is the "
                  "model's context length.")
            exit(1)

    markov_model.generate(args.ofs, args.length, args.width, args.seed)
    args.ofs.close()


if __name__ == "__main__":
    main()

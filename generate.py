import argparse
import sys
from Markov import Model

aparse = argparse.ArgumentParser(
    description="Use an existing Markov model to generate new text of "
                "given length.",
    add_help=False)
aparse.add_argument('--model', dest='ifs', default=sys.stdin,
                    type=argparse.FileType('r', encoding='utf8'),
                    help="Path to the input file containing a json-encoded "
                         "model generated by train.py. Read from stdin by "
                         "default.")
aparse.add_argument('--seed', default=None,
                    help="First C space-separated words to seed the generator, "
                         "where C is the model's context length. Should be "
                         "quote-enclosed if C > 1. Chosen randomly by default.")
aparse.add_argument('--length', type=int, required=True,
                    help="Length of the generated text.")
aparse.add_argument('--output', default=sys.stdout, dest='ofs',
                    type=argparse.FileType('w', encoding='utf8'),
                    help="Path to the output file. Print to stdout by default.")
aparse.add_argument('--help', action="help",
                    help="Display this help message and exit")

args = aparse.parse_args()

mm = Model.load(args.ifs)
if args.length < mm.ctxLength + 1:
    print("Please specify a length greater than model's context length.")
    exit(1)

if args.seed is not None:
    args.seed = args.seed.strip().split()
    if len(args.seed) != mm.ctxLength:
        print("Please specify exactly C words in the seed, where C is the "
              "model's context length.")
        exit(1)

mm.generate(args.ofs, args.length, args.seed)
import argparse
import sys
from Markov import Model

aparse = argparse.ArgumentParser(
    description="Train a Markov model based on text files.",
    add_help=False)
aparse.add_argument('--ctx', type=int, default=1,
                    help="Length of context (number of words). 1 by default")
aparse.add_argument('--input', default=sys.stdin,
                    type=argparse.FileType('r', encoding='utf8'),
                    help="Path to the input file. If both this and " \
                         "--input-dir are ommitted, read from stdin.")
aparse.add_argument('--input-dir', default=None,
                    help="Path to the input directory with .txt files.")
aparse.add_argument('--model', dest='ofs', type=argparse.FileType('w'),
                    default=sys.stdout,
                    help="Path to the output model file. "
                         "Print to stdout by default")
aparse.add_argument('--lc', action="store_true",
                    help="Convert input texts to lower case")
aparse.add_argument('--help', action="help",
                    help="Display this help message and exit")
args = aparse.parse_args()

mm = Model(ctx_length=args.ctx, lower=args.lc)
if args.input_dir is not None:
    import os
    for file in os.listdir(args.input_dir):
        if file.endswith(".txt"):
            fpath = os.path.join(args.input_dir, file)
            with open(fpath, 'r', encoding="utf8") as ifs:
                mm.train(ifs)
else:
    mm.train(args.input)

mm.finalize()
mm.dump(args.ofs)
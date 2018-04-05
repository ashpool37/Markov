import argparse
from Markov import Model

argParser = argparse.ArgumentParser(
    description="Train a Markov model based on text files.")

mm = Model(ctx_length=2)
arg_ifs = open("sonnets.txt", 'r')
arg_ofs = open("model.json", 'w')
mm.train(arg_ifs)
mm.finalize()
mm.dump(arg_ofs)
pass

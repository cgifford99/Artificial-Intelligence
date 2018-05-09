# Artificial-Intelligence
## neural_network.py
Custom neural network built from scratch. Only required library is Numpy.

## data_gen.py
Generates and parses Part-Of-Speech data into an excel spreadsheet. Used in conjunction with pos_tagger.py.
Downloads a 511MB training corpus into script directory. May take several minutes to download based on internet speed.

## pos_tagger.py
Attempts to generate POS tag sequence based on a sentence input by the user. Run data_gen.py first, then this.

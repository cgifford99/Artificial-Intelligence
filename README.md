# Artificial-Intelligence
## neural_network.py
Custom neural network built from scratch. numpy package required.

## data_gen.py
Generates and parses Part-Of-Speech data into an excel spreadsheet. Used in conjunction with pos_tagger.py.
Downloads a 511MB training corpus into script directory. Will take several minutes to download and unzip. Currently no download logs aside from obvious errors. sqlite3, urllib, zipfile and shutil packages required

## pos_tagger.py
Attempts to generate POS tag sequence based on a sentence input by the user. Run data_gen.py first, then this. sqlite3 package required

import logging
import os
import sys
import time
import urllib.request
import xml.etree.ElementTree as etree
import zipfile

from file_utils import ensure_dir
from sqlite_db import SQLite3_DB
from bnc_util import BNC_Utility

# TBH This program actually works very well. Good job - CG 2/11/19
# But holy shit it's built horrendously :( At least it works - CG 9/7/21

# TODO: Rebuild database such that words and part of speech are in separate columns
# TODO: Rebuild parser to user XML parser
# TODO: Rebuild class/inheritance structure, remove globals where necessary

# # planned corpus location
# corpusPath = os.path.dirname(sys.argv[0])
# print(corpusPath)
#
# # corpus document location
# docPath = os.path.join(corpusPath, 'BNC/download/Texts')
#
# # data dictionaries/arrays
# wordPOSCounts = {}
# POSPOSCounts = {}
# POSCounts = {}
# transitionProb = {}
# emissionProb = {}
#
# previousPOS = "START"

# what are common operations that I need to do with this data?
# parsing from the XML files/extracting certain bits of info from the files -> this could be static
# inserting new words + updating the probabilities

# static or non-static:
# if non-static, methods and variables become bound to the class it is written under and can be harder to untangle
# if static, methods and variables can diverge from the original purpose and are generally harder to control
#   under the same principles it was originally written.
# the question I think is, do you need to use a certain method outside the scope of the class it is written under?
# or in other words, is there another purpose for that method beyond its parent class?
# For example, for importCorpus and parseCorpus:
# * I will likely need them for testing purposes

'''
This file generates a SQLite3 database containing useful part-of-speech (POS) data from the British National Corpus (BNC).
This POS data is assembled for use in a Viterbi algorithm calculation to estimate POS tags from any given sentence.
In particular, two tables will provide the bulk of the information necessary to do this task: transition probabilities
    and emission probabilities.
    The transition probability table or more formally, matrix describes the probability of one POS occurring after another.
        For example, the probability of observing a verb then a noun, P(NN|VB) could be 0.0615=6.15%
        vs. the probability of observing a verb then a determiner, P(DT|VB) could be 0.2231=22.31%
    The emission probability table or more formally, matrix describes the probability of a word being a given POS.
        For example, the probability of the word "back" being a verb is 0.0672% vs "back" being an adverb is 1.0446%
    NOTE: Values given above do not reflect values directly found by this program as the underlying dataset is subject to change.
'''


class POS_Data_Generator(BNC_Utility):
    root_path = os.getcwd()
    default_db_path = os.path.join(root_path, 'pos_training.db')
    default_corpus_path = os.path.join(root_path, 'datasets', 'BNC')

    def __init__(self, corpus_path=default_corpus_path, db_path=default_db_path, overwrite=False):
        super().__init__(corpus_path)

        logging.basicConfig()
        self.logger = logging.getLogger("pos-data-generator")
        self.logger.setLevel(logging.DEBUG)

        self.db_path = db_path
        self.sqlite_db = SQLite3_DB(db_path)

        if overwrite:
            self.drop_tables()

        self.create_tables()

        # self.document_path = os.path.join(self.document_path, 'A', 'A0')

    def create_tables(self):
        self.sqlite_db.executeUpdateQuery(
            '''CREATE TABLE if not exists emissionTotals(
                        id INTEGER PRIMARY KEY AUTOINCREMENT, word VARCHAR, pos VARCHAR, count INTEGER
                    )'''
        )
        self.sqlite_db.executeUpdateQuery(
            '''CREATE TABLE if not exists transitionTotals(
                        id INTEGER PRIMARY KEY AUTOINCREMENT, curr_pos VARCHAR, prev_pos VARCHAR, count INTEGER
                    )'''
        )
        self.sqlite_db.executeUpdateQuery(
            '''CREATE TABLE if not exists posTotals(
                        id INTEGER PRIMARY KEY AUTOINCREMENT, pos VARCHAR, count INTEGER
                    )'''
        )
        self.sqlite_db.executeUpdateQuery(
            '''CREATE TABLE if not exists transitionProb(
                        id INTEGER PRIMARY KEY AUTOINCREMENT, curr_pos VARCHAR, prev_pos VARCHAR, probability DOUBLE PRECISION
                    )'''
        )
        self.sqlite_db.executeUpdateQuery(
            '''CREATE TABLE if not exists emissionProb(
                        id INTEGER PRIMARY KEY AUTOINCREMENT, word VARCHAR, pos VARCHAR, probability DOUBLE PRECISION
                    )'''
        )

    def drop_tables(self):
        self.sqlite_db.executeUpdateQuery('DROP TABLE IF EXISTS emissionTotals')
        self.sqlite_db.executeUpdateQuery('DROP TABLE IF EXISTS transitionTotals')
        self.sqlite_db.executeUpdateQuery('DROP TABLE IF EXISTS posTotals')
        self.sqlite_db.executeUpdateQuery('DROP TABLE IF EXISTS transitionProb')
        self.sqlite_db.executeUpdateQuery('DROP TABLE IF EXISTS emissionProb')


def main():

    # recursion limit too low for some documents within corpus; will return error otherwise
    # sys.setrecursionlimit(4000)

    pos_data_generator = POS_Data_Generator(overwrite=True)
    pos_data_generator.import_corpus()

    emission_totals = {}
    transition_totals = {}
    pos_totals = {}
    for word_list in pos_data_generator.parse_corpus():
        # run insert query
        for idx in range(len(word_list)):
            word, pos = word_list[idx]
            # force unambiguous tags
            pos_split = pos.split('-')

            for pos_comp in pos_split:
                emis_key = (word, pos_comp)
                if emis_key not in emission_totals.keys():
                    emission_totals[emis_key] = 0
                emission_totals[emis_key] += 1

            prev_pos = 'START'
            if idx != 0:
                _, prev_pos = word_list[idx - 1]
            for pos_comp in pos_split:
                for prev_pos_comp in prev_pos.split('-'):
                    trans_key = (pos_comp, prev_pos_comp)
                    if trans_key not in transition_totals.keys():
                        transition_totals[trans_key] = 0
                    transition_totals[trans_key] += 1

            for pos_comp in pos_split:
                if pos_comp not in pos_totals.keys():
                    pos_totals[pos_comp] = 0
                pos_totals[pos_comp] += 1

    print('')

    emission_probs = []
    for word, pos in emission_totals.keys():
        if pos not in pos_totals.keys():
            pos_data_generator.logger.error(f'POS "{pos}" found in emission_totals without corresponding pos_totals key')
            continue

        pos_total = pos_totals[pos]
        word_pos_prob = emission_totals[(word, pos)] / pos_total
        emission_probs.append((word, pos, word_pos_prob))

    transition_probs = []
    for pos, prev_pos in transition_totals.keys():
        if pos not in pos_totals.keys():
            pos_data_generator.logger.error(f'POS "{pos}" found in transition_totals without corresponding pos_totals key')
            continue

        pos_total = pos_totals[pos]
        trans_pos_prob = transition_totals[(pos, prev_pos)] / pos_total
        transition_probs.append((pos, prev_pos, trans_pos_prob))

    pos_data_generator.sqlite_db.executeUpdateManyQuery(
        'INSERT INTO emissionProb (word, pos, probability) VALUES (?, ?, ?)', emission_probs)

    pos_data_generator.sqlite_db.executeUpdateManyQuery(
        'INSERT INTO transitionProb (curr_pos, prev_pos, probability) VALUES (?, ?, ?)', transition_probs)


if __name__ == '__main__':
    start = time.time()
    main()
    timeTaken = time.time() - start
    convertedTime = time.strftime("%H:%M:%S", time.gmtime(timeTaken))
    print("--- Time taken: %s ---" % convertedTime)

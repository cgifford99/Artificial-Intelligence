import logging
import os
import time
import re

from sqlite_db import SQLite3_DB

# Alright, this program works flawlessly with 1 sentence that I know of. Otherwise it crashes ;)
# I am leaving the program to die unfortunately as I have no desire to continue working on it
# until I learn more about viterbi
# - CG 2/11/19

# Hey! Trying to resurrect this program a bit with my text analytics class
# Here's some notes:
# Conjunctions don't work (notice the irony there)


class POS_Tagger(object):
    default_db_path = f'{os.getcwd()}\\pos_training.db'

    def __init__(self, db_path=default_db_path):
        logging.basicConfig()
        self.logger = logging.getLogger("pos-tagger")
        self.logger.setLevel(logging.INFO)

        self.db_path = db_path
        self.sqlite_db = SQLite3_DB(db_path)

        transitionProbRaw = self.sqlite_db.executeRetrievalQuery("SELECT curr_pos, prev_pos, probability FROM transitionProb")
        self.transitionProbability = {(transitionRow[0], transitionRow[1]): transitionRow[2] for transitionRow in transitionProbRaw}

        emissionProbRaw = self.sqlite_db.executeRetrievalQuery("SELECT word, pos, probability FROM emissionProb")
        self.emissionProbability = {(emissionRow[0], emissionRow[1]): emissionRow[2] for emissionRow in emissionProbRaw}

        self.word_driven_emissprob = {}
        for word, pos in self.emissionProbability:
            if word not in self.word_driven_emissprob.keys():
                self.word_driven_emissprob[word] = []
            self.word_driven_emissprob[word].append(pos)
            

    def viterbi(self, wordList, sentenceTagRange):
        '''
        I've implemented a modified version of the Viterbi algorithm for HMM's
        A traditional implementation of the Viterbi algorithm includes an initial probability matrix
        containing probabilities for each POS tag to be located at the beginning of a sentence, hence initial.
        I've merged that matrix with the transition probability matrix and included a new POS tag "START".

        It's main purpose is to generate the most probable sequence of POS tags for a given sequence of words
        and a subset of pre-determined possible tags from the database.
        :param wordList:
        :param sentenceTagRange:
        :return:
        '''
        final_cell_prob = []
        prev_max_path_prob_arr = []
        # iterate through each state
        for i in range(len(sentenceTagRange)):
            path_prob_arr = []
            # iterate through a subset of pos tags for each state
            # calculate the probability for each possible pos tag in context of the previous tag
            for j in range(len(sentenceTagRange[i])):
                emis_key = (wordList[i], sentenceTagRange[i][j])
                emission_prob = self.emissionProbability.get(emis_key, 0)  # P(word_i|pos_ij)

                if i == 0:
                    # initialization step
                    trans_key = (sentenceTagRange[i][j], "START")
                    transmission_prob = self.transitionProbability.get(trans_key, 0)  # P(pos_ij|"START")
                    path_prob_arr.append(transmission_prob * emission_prob)
                else:
                    path_cell_arr = []
                    # calculate all the probabilities for a given state given all of the previous word's probabilities
                    for prev_state in sentenceTagRange[i - 1]:
                        trans_key = (sentenceTagRange[i][j], prev_state)
                        transmission_prob = self.transitionProbability.get(trans_key, 0)  # P(pos_ij|prevpos_ik)
                        path_cell_arr.append(transmission_prob * emission_prob)
                    path_prob_arr.append(path_cell_arr)

            maxed_path_prob_arr = []
            if i == 0:
                # initialization step
                maxed_path_prob_arr = path_prob_arr
            else:
                for a in range(len(path_prob_arr)):
                    max_func_arg = []
                    for b in range(len(prev_max_path_prob_arr)):
                        max_func_arg.append(prev_max_path_prob_arr[b] * path_prob_arr[a][b])
                    maxed_path_prob_arr.append(max(max_func_arg or [0]))
            prev_max_path_prob_arr = maxed_path_prob_arr
            final_cell_prob.append(maxed_path_prob_arr or [0])
        return final_cell_prob

    @staticmethod
    def tokenize_sentence(sentence):
        # TODO: Improve tokenization method beyond a regex.
        #   Maybe look into the libpostal tokenization process using the lexer generator.
        # TODO: Contractions
        word_list = re.findall(r"[\w'\-\–,]+", sentence)
        word_list = [word.lower() for word in word_list]
        return word_list

    def tag_sentence(self, word_sequence):
        self.logger.debug("Calculating parts-of-speech...")
        sentence_tag_range = self.calc_whole_sentence_pos_range(word_sequence)
        
        final_cell_prob = self.viterbi(word_sequence, sentence_tag_range)

        tag_sequence = []
        for index in range(len(final_cell_prob)):
            if not final_cell_prob[index]:
                self.logger.error('Undefined probability found from finalCellProbability')
                continue
            max_val = max(final_cell_prob[index])
            max_idx = final_cell_prob[index].index(max_val)
            tag_sequence.append(sentence_tag_range[index][max_idx])

        return tag_sequence
    
    def calc_whole_sentence_pos_range(self, word_sequence):
        sentence_tag_range = []
        for word in word_sequence:
            word_match_results = []
            if word in self.word_driven_emissprob:
                word_match_results = self.word_driven_emissprob[word]

            filtered_match_results = []
            for pos in word_match_results:
                if pos == 'UNC' and len(word_match_results) > 1:
                    continue
                filtered_match_results.append(pos)

            word_tag_range = []
            word_tag_range.extend(filtered_match_results)

            if not word_tag_range:
                # TODO: Implement system to add new words to database when found. Tag with UNC for now
                word_tag_range = ["UNC"]
            sentence_tag_range.append(word_tag_range)
        return sentence_tag_range


def main():
    pos_tagger = POS_Tagger()

    # while True:
        # sentence = input("Insert a sentence for part-of-speech tagging (Enter 'q' to quit): ")
        # if sentence.strip().lower() is 'q':
        #     break
    sentence = 'is a condition caused by a virus called hiv human immuno deficiency virus' # NOTE: Temporary
    wordList = pos_tagger.tokenize_sentence(sentence)
    tagSequence = pos_tagger.tag_sentence(wordList)

    print(' '.join(f'{wordList[index]}[{tagSequence[index]}]' for index in range(len(tagSequence))))
    exit() # NOTE: Temporary


if __name__ == '__main__':
    start = time.time()
    main()
    timeTaken = time.time() - start
    convertedTime = time.strftime("%H:%M:%S", time.gmtime(timeTaken))
    print("--- Time taken: %s ---\n" % convertedTime)

import logging
import os
import sys

from bnc_util import BNC_Utility
from pos_tagger import POS_Tagger

class POS_Tagger_Test():
    root_path = os.getcwd()
    corpus_path = os.path.join(root_path, 'datasets', 'BNC')
    test_num_limit = 100

    def test_pos_from_file(self):
        pos_tagger = POS_Tagger()
        bnc_util = BNC_Utility(self.corpus_path)
        bnc_util.document_path = os.path.join(bnc_util.document_path, 'A', 'A0')

        positive_matches = 0
        negative_matches = 0
        bnc_util.logger.setLevel(logging.DEBUG)
        for corpus_tagged_words in bnc_util.parse_corpus():
            base_tag_sequence = [c5_tag for _, c5_tag in corpus_tagged_words]
            base_word_sequence = [word for word, _ in corpus_tagged_words]
            base_str = ' '.join(base_word_sequence)
            bnc_util.logger.debug(f'Testing sentence {positive_matches+negative_matches}: {base_str}')
            base_str_tokenized = pos_tagger.tokenize_sentence(base_str)
            generated_tag_sequence = pos_tagger.tag_sentence(base_str_tokenized)
            # generated_str_tagged = ' '.join(f'{base_word_sequence[index]}[{generated_tag_sequence[index]}]' for index in range(len(generated_tag_sequence)))
            # base_str_tagged = ' '.join([f'{word}[{c5_attr}]' for word, c5_attr in corpus_tagged_words])
            # adjust to assertSimilar where if one pos is contained in another
            if self.isPosResultEqualRelaxed(base_tag_sequence, generated_tag_sequence):
                positive_matches += 1
            else:
                negative_matches += 1

            if positive_matches + negative_matches >= self.test_num_limit:
                break

        print(f'''Total sequences tested: {positive_matches+negative_matches}\nPositive matches: {positive_matches}\nNegative matches: {negative_matches}\nAccuracy: {(positive_matches/(positive_matches+negative_matches))*100}%''')

    def isPosResultEqualRelaxed(self, base_case_seq, generated_seq):
        if len(base_case_seq) != len(generated_seq):
            print('ERROR: Divergence detected. Mismatch sequence length')
            return False
        sequence_match = True
        for tag_idx in range(len(base_case_seq)):
            base_case_tag = base_case_seq[tag_idx]
            generated_tag = generated_seq[tag_idx]
            if 'unc' in base_case_tag.lower():
                continue
            if ('-' in generated_tag and base_case_tag in generated_tag) or ('-' in base_case_tag and generated_tag in base_case_tag):
                continue
            elif base_case_tag != generated_tag:
                print(f'WARNING: Mismatch tags found on idx {tag_idx}: base:{base_case_tag}, generated:{generated_tag}, for sequences: base: {base_case_seq}, generated: {generated_seq}')
                sequence_match = False
        return sequence_match

    def isPosResultEqual(self, base_case_seq, generated_seq):
        if len(base_case_seq) != len(generated_seq):
            print('ERROR: Divergence detected. Mismatch sequence length')
            return False
        sequence_match = True
        for tag_idx in range(len(base_case_seq)):
            base_case_tag = base_case_seq[tag_idx]
            generated_tag = generated_seq[tag_idx]
            if base_case_tag != generated_tag:
                print(f'WARNING: Mismatch tags found on idx {tag_idx}: base:{base_case_tag}, generated:{generated_tag}, for sequences: base: {base_case_seq}, generated: {generated_seq}')
                sequence_match = False
        return sequence_match

if __name__ == '__main__':
    tagging_test = POS_Tagger_Test()
    tagging_test.test_pos_from_file()

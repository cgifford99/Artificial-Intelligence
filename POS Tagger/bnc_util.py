import logging
import os
import sys
import time
import xml.etree.ElementTree as etree
import urllib.request
import zipfile

from file_utils import ensure_dir

logging.basicConfig()


class BNC_Utility(object):

    def __init__(self, corpus_path):
        self.logger = logging.getLogger('bnc-utility')
        self.logger.setLevel(logging.DEBUG)

        self.corpus_path = corpus_path
        ensure_dir(self.corpus_path)
        self.document_path = os.path.join(self.corpus_path, 'download', 'Texts')  # directory created by corpus archive

    def import_corpus(self, overwrite=False):
        # Download corpus for training into corpus_path directory
        # BNC Publication Info can be found at: https://ota.bodleian.ox.ac.uk/repository/xmlui/handle/20.500.12024/2554
        # Archive download can be found at: https://ota.bodleian.ox.ac.uk/repository/xmlui/bitstream/handle/20.500.12024/2554/2554.zip?sequence=3&isAllowed=y
        ESTIMATED_ARCHIVE_SIZE = 550 * pow(10, 6)  # 551 MB download size as of 9/9/21
        bnc_zip_path = os.path.join(self.corpus_path, 'BNC.zip')
        sample_document_path = os.path.join(self.corpus_path, 'download', 'Texts', 'K', 'KS', 'KSW.xml')
        if overwrite:
            os.remove(self.corpus_path)

        if not os.path.exists(bnc_zip_path) and not os.path.exists(sample_document_path):
            self.logger.debug('Corpus not found. Downloading...')
            urllib.request.urlretrieve(
                'https://ota.bodleian.ox.ac.uk/repository/xmlui/bitstream/handle/20.500.12024/2554/2554.zip?sequence=3&isAllowed=y',
                bnc_zip_path, self.reporthook
            )
            sys.stdout.write('\n\r')
        else:
            self.logger.debug('Corpus found. Will not download.')
        if os.path.exists(bnc_zip_path) and os.stat(bnc_zip_path).st_size < ESTIMATED_ARCHIVE_SIZE:
            self.logger.warning("Existing BNC Archive is of unexpected size. Archive may not be complete or corrupted.")
        if not os.path.exists(sample_document_path):
            self.logger.debug('Extracting corpus...')
            zipRef = zipfile.ZipFile(bnc_zip_path, 'r')
            zipRef.extractall(self.corpus_path)
            zipRef.close()
            self.logger.debug('Finished extracting corpus!')
        else:
            self.logger.debug('Corpus previously unzipped. Will not continue.')

        os.chmod(self.corpus_path, 777)
        if os.path.exists(bnc_zip_path):
            os.remove(bnc_zip_path)

    @staticmethod
    # Thanks to https://blog.shichao.io/2012/10/04/progress_speed_indicator_for_urlretrieve_in_python.html
    def reporthook(count, blockSize, totalSize):
        global start_time
        if count == 0:
            start_time = time.time()
            return
        duration = time.time() - start_time
        progress_size = int(count * blockSize)
        speed = int(progress_size / (1024 * duration + 0.000001))
        percent = min(int(count * blockSize * 100 / totalSize), 100)
        sys.stdout.write("\r...%d%%, %d MB, %d KB/s, %d seconds passed" %
                         (percent, progress_size / (1024 * 1024), speed, duration))
        sys.stdout.flush()

    def parse_corpus(self):
        for dirPath, dirNames, fileNames in os.walk(self.document_path):
            for fileName in fileNames:
                self.logger.debug("\rParsing file %s" % fileName)
                with open(os.path.join(dirPath, fileName), encoding="utf-8") as file:
                    tree = etree.parse(file)
                    root = tree.getroot()
                    for sentence_elem in root.iter('s'):
                        words = []
                        for word_elem in sentence_elem.findall('w'):
                            attr_dict = word_elem.attrib
                            c5_attr = attr_dict.get('c5') or 'UNC'
                            word = word_elem.text
                            if not word:
                                continue
                            word = word.lower().strip().replace(r'[$%°½©+&#@^]', '')
                            if '/' in word:
                                words.extend([(split_word, c5_attr) for split_word in word.split('/')])
                            # elif '-' in word and c5_attr == 'CRD':
                            #     still considering
                            #     words.extend([(split_word, c5_attr) for split_word in word.split('-')])
                            else:
                                words.append((word, c5_attr))
                        yield words

                    file.close()

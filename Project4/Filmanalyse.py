import re
import glob
import operator
from time import time
from collections import defaultdict
from math import log
from itertools import zip_longest
from heapq import nlargest

class Filmanalyse:

    def __init__(self):
        f_stop_words = open('stop_words.txt')
        stop_words = f_stop_words.read().split()
        f_stop_words.close()
        self.stop_words = set(stop_words)
        #self.n_gram = n_gram #lengden på n_gram
        self.neg_file_list = glob.glob('data/alle/train/neg/*.txt')
        self.pos_file_list = glob.glob('data/alle/train/pos/*.txt')
        self.pos_reviews = len(self.pos_file_list)
        self.neg_reviews = len(self.neg_file_list)
        self.total_reviews = len(self.neg_file_list) + len(self.pos_file_list)
        self.p_words, self.n_words, self.t_words = {}, {}, defaultdict(int)

#del 1
    def read_from_document(self,file):
        f = open(file, encoding = 'utf-8')
        content = f.read().lower()
        words = re.sub('[^0-9a-zA-Z]+', ' ', content).split()
        f.close()
        #del 6
        #if self.n_gram > 0:
            #words += ["_".join(words[x:x + self.n_gram]) for x in range(0, len(words) - (self.n_gram + 1))]
#del 3
        return set([word for word in words if word not in self.stop_words])

#del 2
    def read_all_files(self):
        pos_rev = glob.glob("data/alle/train/pos/*.txt")
        pos_words = Filmanalyse.count_words(self,pos_rev)
        top_pos_words = dict(sorted(pos_words.items(), key=operator.itemgetter(1), reverse=True)[:25])

        neg_rev = glob.glob("data/alle/train/neg/*.txt")
        neg_words = Filmanalyse.count_words(self,neg_rev)
        top_neg_words = dict(sorted(neg_words.items(), key=operator.itemgetter(1), reverse=True)[:25])

        return top_pos_words, top_neg_words

    #Hjelpefunksjon
    def count_words(self,reviews):
        words = {}
        for rev in reviews:
            words_in_rev = Filmanalyse.read_from_document(self,rev)
            for word in words_in_rev:
                if (word not in words) and (word is not None):
                    words[word] = 1
                elif (word is not None):
                    words[word] += 1
        return words

#del 4
    def most_informative_words(self):
        for pos_f, neg_f in zip_longest(self.pos_file_list, self.neg_file_list):
            pos_list = self.read_from_document(pos_f)
            neg_list = self.read_from_document(neg_f)
            for pos_word, neg_word in zip_longest(pos_list, neg_list):
                if pos_word in self.p_words:
                    self.p_words[pos_word] += 1
                    self.t_words[pos_word] += 1
                elif pos_word not in self.p_words and pos_word is not None:
                    self.p_words[pos_word] = 1
                    self.t_words[pos_word] += 1
                if neg_word in self.n_words:
                    self.n_words[neg_word] += 1
                    self.t_words[neg_word] += 1
                elif neg_word not in self.n_words and neg_word is not None:
                    self.n_words[neg_word] = 1
                    self.t_words[neg_word] += 1

        pos_words_info, neg_words_info = {}, {}
        for p_word, n_word in zip_longest(self.p_words, self.n_words):
            pos_prosent = self.t_words[p_word] / self.total_reviews
            neg_prosent = self.t_words[n_word] / self.total_reviews
#del 5
            if p_word is not None and pos_prosent > 0.02:
                pos_words_info[p_word] = self.p_words[p_word] / self.t_words[p_word]
            if n_word is not None and neg_prosent > 0.02:
                neg_words_info[n_word] = self.n_words[n_word] / self.t_words[n_word]
        top_pos = nlargest(25, pos_words_info, key=pos_words_info.get)
        top_neg = nlargest(25, neg_words_info, key=neg_words_info.get)
        return top_pos, top_neg

    def prune(self):
        pass


class Classification():
    def __init__(self):
        self.analyzer = Filmanalyse()


    def train(self):
        self.analyzer.most_informative_words()


    def classify_file(self, file):
        words = self.analyzer.read_from_document(file)
        positivity = 0
        negativity = 0
        for word in words:
            if word in self.analyzer.p_words:
                positivity += log(self.analyzer.p_words[word]/self.analyzer.pos_reviews)
                if word not in self.analyzer.n_words:
                    negativity += log(0.02)
            if word in self.analyzer.n_words:
                negativity += log(self.analyzer.n_words[word]/self.analyzer.neg_reviews)
                if word not in self.analyzer.p_words:
                    positivity += log(0.02)
        if positivity > negativity:
            return True
        elif negativity > positivity:
            return False
        else:
            pass

    def evalute_files(self, path):
        count = 0
        total = 0
        for file in glob.glob(path):
            guess = self.classify_file(file)
            if guess:
                count += 1
            total += 1
        return count/total

def main():


    film = Filmanalyse()

    pos_words, neg_words = film.read_all_files()
    print("Positive ord: ")
    print(pos_words)
    print("Negative ord: ")
    print(neg_words)

    pos_info, neg_info = film.most_informative_words()
    print("Positive informative ord: ")
    print(pos_info)
    print("Negative informative ord: ")
    print(neg_info)

    start = time()

    classify_object = Classification()
    classify_object.train()
    pos_path = "data/alle/test/pos/*"
    neg_path = "data/alle/test/neg/*"
    pos_result = classify_object.evalute_files(pos_path)
    neg_result = 1 - classify_object.evalute_files(neg_path)
    print("Positivt resultat: " + str(pos_result))
    print("Negativt resultat: " + str(neg_result))

    end = time()

    print('Tid: ' + str(end-start))

main()
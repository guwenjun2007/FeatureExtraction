
# coding: utf-8

# In[2]:

import os,copy
import re
import csv
import nltk
import string

class TextFeature:
    
    def __init__(self):
        
        self.symbols = "!\"#$%&()*+,_-./:;<=>?@[\]^`{|}~\\"
        self.booklist = [] #list of names of the books in the file
        self.overalldic = {} #all unique words in all the books
        self.sepdics = [] #all unique word frequency in each book       
        self.maxSentenceLen = 0 # longest sentence in the folder
   
    
    def tokenize(self,path):
        #calculate and fill booklist, overalldic
        # booklist: list of names of the books in the file
        # overalldic: all unique words in all the books; can be further used to analyze the data such as tf-idf
        filelist = os.listdir(path)
        # pick the file containing '.txt', list them in "booklist"
        for f in filelist:
            if '.txt' in f:
                self.booklist.append(f)
        
        os.chdir(path)# change the current path to the desired path 
        
        # create the overall dictionary first
        for i in self.booklist:
            # read everyline of the document into "lines"
            fi = open(i,'r')
            lines = fi.readlines()
            book_content = fi.read()
            fi.close()
            for l in lines:
                # for each line, match all the alphanumber                
                words = re.findall(r"[\w']+", l)               
                for w in words:
                    # process each word to get rid of non-ASCII, numbers and etc.
                    processedword = self.singleWordProcess(w)
                    # word count and put the result in overalldict
                    if processedword != '':
                        if self.overalldic.has_key(processedword):
                            self.overalldic[processedword] += 1
                        else:
                            self.overalldic[processedword] = 1        
                            
    
    def get_sepdics(self, path):
        # get sepdics: all unique word frequency in each book    
        # input: path of the folder
        # output: spedics #all unique word frequency in each book
        csv_path = path + '/ngram.csv'
        open(csv_path, 'w').close()
        blankdic = {}	# a template dictionary with all occurences equal to 0
        
        for k in self.overalldic.keys():
            blankdic[k] = 0 # initialization 
        
        for i in self.booklist:
            tmpdic = copy.copy(blankdic)
            #read books by lines and seperate words from each line
            fi = open(i, 'r')
            lines = fi.readlines()
            fi.close()
            #read books and pass the context for sentence calculation
            fi = open(i, 'r')
            book_content = fi.read()
            fi.close()
            for l in lines:
                #words = l.split()
                words = re.findall(r"[\w']+", l)
                for w in words:
                    processedword = self.singleWordProcess(w)
                    if processedword != '':
                        tmpdic[processedword] += 1
            self.sepdics.append(tmpdic)# put the word frequency in each 
            self.ngram_richness(tmpdic, i, csv_path) #write 3 features into ngram.csv  
            self.sentenceLengthDistribution(path, book_content)
        self.clearPlural()  #clear ngram.csv before writing
    
    
    def clearPlural(self): # clear plural and third person singular 
        # +s and +es is considered
        for k in self.overalldic.keys():
            if(self.overalldic.has_key(k)):
                if self.overalldic.has_key(k+'s'):
                    self.overalldic[k] += self.overalldic[k+'s']
                    self.overalldic.pop(k+'s')
                    for dic in self.sepdics:
                        dic[k] += dic[k+'s']
                        dic.pop(k+'s')
                if self.overalldic.has_key(k+'es'):
                    self.overalldic[k] += self.overalldic[k+'es']
                    self.overalldic.pop(k+'es')
                    for dic in self.sepdics:
                        dic[k] += dic[k+'es']
                        dic.pop(k+'es')

    
    def ngram_richness(self, tmpdic, book,path):
        # get the three features of each file
        # input: the file name, and the word frequecy of the file
        # output: ngram.cvs includes three features
        #1. Hapax Legomena1(n-gram): Number of words that occur exactly once.(Normalized by number of unique words)
        #2. Dis Legomena1 Number of words that occurs exactly twice.(Normalized by number of unique words)
        #3. Vocabulary Richness: Total number of unique words.(Normalized by number of words.)
        totalCount = 0
        uniqueCount = 0
        once = 0
        twice = 0
        for k, v in tmpdic.iteritems():
            if v > 0:
                totalCount += v
                uniqueCount += 1
            if v == 1:
                once += 1
            elif v == 2:
                twice += 1
        once_rate = once / float(uniqueCount) # featue 1
        twice_rate = twice / float(uniqueCount) # feature 2
        unique_rate = uniqueCount / float(totalCount) # feature 3
        book_no = book.split('_')[0]

        # write feature into .csv file
        row = [book_no,
        '{:.9f}'.format(once_rate), 
        '{:.9f}'.format(twice_rate), 
        '{:.9f}'.format(unique_rate),]# specify the precision if necessray
        with open(path, 'a') as f:
            writer = csv.writer(f)
            writer.writerow(row)
            
    
    def singleWordProcess(self,word):
        #input: String, raw single word
        #output: String, processed word getting rid of non-ASCII, numbers and etc.
        word = word.lower()
        # clear symbols from the word 
        for i in self.symbols:
            word = word.replace(i,'')
       
        # non-ASCII and numbers
        for c in word:
            if ord(c) >= 128:
                word = word.replace(c, '')
            if c.isdigit():
                return ''
        #if "xx" in word:
            #return ''
        word = word.strip()
        #if len(word) < 3:
        #    return ''
        #possessive case
        if len(word) > 1:
            if word[0] == "'":
                word = word.replace("'",'')
            ind = word.find("'")
            if(ind != -1):
                word = word[:ind]
            if len(word) > 1:
                return word
            else:
                return ''
        else:
            return ''
    
    
    def sentenceLengthDistribution(self, path, book_content):
        #usage: get Sentence Length Distribution(how many words per sentence)
        #input: path, content of the file
        #output: length distribution of sentences in .csv file
        
        res_path = path + '/sentence_length_distribute.csv'
        tmp = {} #length of word --> frequency
        row = [] #frequency of word of length i, i in index of the list
        totalSentence = 0
        printable = set(string.printable)
        text = filter(lambda x: x in printable, book_content)
        
        #use Python natural language package to pick up sentences from the book
        sentences = nltk.sent_tokenize(text)
        
        for sentence in sentences:
            words = re.findall(r"[\w']+", sentence)
            if len(words) > 0:
                totalSentence += 1
                if tmp.has_key(len(words)):
                    tmp[len(words)] += 1
                else:
                    tmp[len(words)] = 1
        
        #iterate k, v pairs in the dict and write the frequency into a list
        maxlen = 1
        longest_sentence = 0
        for k, v in tmp.iteritems():
            if v > maxlen:
                maxlen = v
            if k > longest_sentence:
                longest_sentence = k
        
        #print "longest sentence: " + str(longest_sentence)
        for i in xrange(maxlen + 1):
            if (tmp.has_key(i)):
                row.append(tmp.get(i))
            else:
                row.append(0)
        i = maxlen
        if maxlen > self.maxSentenceLen:
            self.maxSentenceLen = maxlen
        
        #get rid of '0' length sentence
        while row[i] == 0 and i > 0:
            del row[i]
            i -= 1
        del row[0]
        row.append(totalSentence)
        for i in xrange(len(row) - 1):
            row[i] = '{:.9f}'.format(row[i] / float(totalSentence))

        with open(res_path, 'a') as f:
            writer = csv.writer(f)
            writer.writerow(row)

    
    def addZeros(self, path):
        #usage: padding all the files in a .csv file to be the same length
        #input: path of the file
        #output:padded .csv file
        max_row_length = 0
        rows = []
        with open(path, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                rows.append(row)
                if len(row) > max_row_length:
                    max_row_length = len(row)
        #print 'length of row = ' + str(max_row_length)
        for row in rows:
            if len(row) < max_row_length:
                for i in xrange(max_row_length - len(row)):
                    row.append('0.000000000')
        open(path, 'w').close()
        with open(path, 'w') as f:
            writer = csv.writer(f)
            for row in rows:
                writer.writerow(row)

    
    def wordLengthDistribution(self, path):
        #usage: find the word length distribution of each file in the folder
        #input: path of the folder
        #output: .csv file saves word length distribution

        write_path = path + '/word_length_distribution.csv'
        open(write_path, 'w').close()
        word_length_dict = {} #word length --> frequency of certain length of word
        for i in self.booklist:
            fi = open(i,'r')
            lines = fi.readlines()
            fi.close()
            no_word = 0
            for l in lines:
                words = re.findall(r"[\w']+", l)
                for word in words:
                    if word_length_dict.has_key(len(word)):
                        word_length_dict[len(word)] += 1
                    else:
                        word_length_dict[len(word)] = 1
            max_word_length = 0
            for k, v in word_length_dict.iteritems():
                no_word += v
                if k > max_word_length:
                    max_word_length = k
            #iterate  and write the frequency into a list
            word_length_list = []
            for i in xrange(1, max_word_length):
                if word_length_dict.has_key(i):
                    word_length_list.append(
                        '{:.9f}'.format(word_length_dict.get(i) / float(no_word))
                        )
                else:
                    word_length_list.append(
                        '0.000000000'
                        )
            with open(write_path, 'a') as f:
                writer = csv.writer(f)
                writer.writerow(word_length_list)

    
    def pronoun_conjunction_distribution(self, path):
        # get the pronoun and conjunction distribution
        # input: .txt files
        # output: two .csv files save pronoun and conjunction word frequency
        
        #dictionary of pronous and conjunctions can be modified in need
        pronouns = set(["i", "you", "he", "she", "it", "we", "they"])
        conjunctions = set(["for", "and", "nor", "but", "or", "yet", "so"])
        printable = set(string.printable)

        write_path_pronouns = path + '/pronouns_distribution.csv'
        write_path_conjunctions = path + '/conjunctions_distribution.csv'
        open(write_path_pronouns, 'w').close()
        open(write_path_conjunctions, 'w').close()

        for i in self.booklist:
            
            fi = open(i,'r')
            text = filter(lambda x: x in printable, fi.read())
            fi.close()
            sentences = nltk.sent_tokenize(text)
            no_sentence = 0
            pronouns_frelist = []
            conjunction_frelist = []
            
            for sentence in sentences:
                
                no_sentence += 1
                #frequency of pronouns and conjunctions in each sentence
                pronouns_fre = 0
                conjunction_fre = 0
                words = re.findall(r"[\w']+", sentence)
                
                for w in words:
                    processedword = self.singleWordProcess(w)
                    if processedword in pronouns:
                        pronouns_fre += 1
                    if processedword in conjunctions:
                        conjunction_fre += 1
                #write frequency distribution into lists
                pronouns_frelist.append(pronouns_fre)
                conjunction_frelist.append(conjunction_fre)
            
            pronouns_dislist = self.fre_to_distribution(pronouns_frelist)
            conjunction_dislist = self.fre_to_distribution(conjunction_frelist)
            pronouns_dislist[:] = ['{:.9f}'.format(x / float(no_sentence)) for x in pronouns_dislist]
            conjunction_dislist[:] = ['{:.9f}'.format(x / float(no_sentence)) for x in conjunction_dislist]

            with open(write_path_pronouns, 'a') as f:
                writer = csv.writer(f)
                writer.writerow(pronouns_dislist)
            with open(write_path_conjunctions, 'a') as f:
                writer = csv.writer(f)
                writer.writerow(conjunction_dislist)
    
    
    def fre_to_distribution(self, my_list):
        # transfer frequency to distribution, return index of distribution list 
        # which is the length or frequency of pronouns or conjunctions in each sentence
        # input: frequency list
        # output: distribution list
      
        max_ele = max(my_list)
        my_distribution_dict = {}
        for ele in my_list:
            if my_distribution_dict.has_key(ele):
                my_distribution_dict[ele] += 1
            else:
                my_distribution_dict[ele] = 1
        distribution = []
        for i in xrange(max_ele + 1):
            distribution.append(0)
        for k, v in my_distribution_dict.iteritems():
            distribution[k] = v
        return distribution


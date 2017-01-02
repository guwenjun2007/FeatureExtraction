
# this file shows how to use the class "TextFeature" to extract following seven features:
#1. Hapax Legomena: Number of words that occur exactly once normalized by number of unique words.
#2. Dis Legomena: Number of words that occur exactly twice normalized by number of unique words.
#3. Vocabulary Richness: Total number of unique words normalized by number of words.
#4. Sentence Length Distribution: Lengths of sentences in the text normalized by number of sentences.
#5. Word Length Distribution: Lengths of the words in the text normalized by  number of words.
#6. Pronoun Distribution: Occurrences of nominative pronouns per sentence normalized by number of sentences.
#7. Conjunction Distribution: Occurrences of conjunctions per sentence normalized by number of sentences.

# the example data is the two book.txt files in "books" folder
# output files are .csv files in the "books" folder

# for detailed application of the file, please read "InstructionOfFeature.txt"
__author__ = 'Wenjun Gu'

from feature import TextFeature
import os
import collections

def main():
    # specify the path of the folder in your file
    path = 'E:/books'
    
    # instantialize an object
    books = TextFeature()
    
    # tokenize the files in the folder for the attribute of the objects
    books.tokenize(path)
    
    #1. get the sepcific word frequency of each files for the attribute of the objects
    #2. extract feature 1, 2, 3 and save them in ngram.csv
    #3. extract feature 4 and save it in sentence_length_distribute.csv, the mean/ variance can be futher calculated if needed
    #       1.can be seperated with 2.and 3.by slightly change the corresponding functions in the TextFeature 
    #       class if necessary in the future.
    books.get_sepdics(path)
    
    # extract feature 5. and save it in word_length_distribution.csv
    books.wordLengthDistribution(path)
    
    # extract feature 6. and 7., save them in pronouns_distribution.csv and conjunctions_distribution.csv, respectively.
    #        extraction of these two features can be seperated by slightly change the corresponding functions 
    #        in the TextFeature class if necessary in the future.
    #        further modification is available if want to extract verbs distribution by supplying verb dictionary.
    books.pronoun_conjunction_distribution(path)

if __name__ == "__main__":
    main()





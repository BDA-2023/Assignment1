"""
    This file contains an implementation of the first pass (aka preprocessing step) for the A-priori algorithm
"""

class FirstPass:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = []

    ''' 
        Read and process dataset file
        @param: itemset_counts, all the unique authors and their respective occurences
        @param: min_support, the minimum threshold for an group's occurence also known as "s" (not used in this version of a-priori)
        @param: k, the maximum group size of authors (not used in this version of a-priori)
        @optional param: max_articles, the maximum articles to read from the dataset (default=100000)
    '''
    def process_file(self, itemset_counts, min_support, k, max_articles = 100000):
        with open(self.file_path, 'r') as file:
            i = 0
            for line in file:
                if i >= max_articles: # max_articles limit
                    return
                i += 1
                line = line.strip()
                if line:  # Check if the line is not empty
                    authors = self.get_authors_from_line(line)
                    self.data.append(authors)
                    self.count_itemsets(itemset_counts, authors)

    ''' 
        Retrieve author from line
        @param: line, current line in the dataset file
    '''
    def get_authors_from_line(self, line):
        authors = line.split(",")
        authors = authors[:-1]  # Delete the last empty string because of the trailing comma
        authors = frozenset(authors) # Remove duplicate authors
        return authors
    
    """
        Count the occurence of every author in the dataset
        @param: itemset_counts, all the unique authors and their respective occurences
        @param: itemset_counts, the authors from a line in the dataset
        pre: author is not mentioned twice because itemset is a set
        post: counts the occurrences of every itemset
    """
    def count_itemsets(self, itemset_counts, itemset):
        for item in itemset:
            item = frozenset([item])
            if item in itemset_counts:
                itemset_counts[item] += 1
            else:
                itemset_counts[item] = 1

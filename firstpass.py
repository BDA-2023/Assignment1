
class FirstPass:
    def __init__(self, file_path):
        self.file_path = file_path
        #self.authors_translation_table = dict(int) # index of authors_counts per author 
        self.data = []

    def process_file(self, itemset_counts, min_support, k, max_articles = 100000):
        with open(self.file_path, 'r') as file:
            i = 0
            for line in file:
                if i >= max_articles:
                    return
                i += 1
                line = line.strip()
                if line:  # Check if the line is not empty
                    authors = self.get_authors_from_line(line)
                    self.data.append(authors)
                    self.count_itemsets(itemset_counts, authors)

    def remove_infrequent_authors(self, itemset_counts, min_support):
        # Create a list to store authors to be removed
        authors_to_remove = []

        # Iterate through the itemset_counts dictionary
        for author, count in itemset_counts.items():
            if count < min_support:
                # Add the author to the removal list
                authors_to_remove.append(author)

        # Remove authors from the itemset_counts dictionary
        for author in authors_to_remove:
            del itemset_counts[author]

    def get_authors_from_line(self, line):
        authors = line.split(",")
        authors = authors[:-1]  # Delete the last empty string because of the trailing comma
        authors = frozenset(authors) # Remove duplicate authors
        return authors
    
    """
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



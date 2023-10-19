class FirstPass:
    def __init__(self, file_path):
        self.file_path = file_path
        self.authors_translation_table = {}
        self.authors_counts = {}
        self.data = []

    def process_file(self):
        with open(self.file_path, 'r') as file:
            for line in file:
                line = line.strip()
                if line:  # Check if the line is not empty
                    authors = self.get_authors_from_line(line)
                    self.data.append(authors)
                    self.build_authors_dict(authors)
        #print(self.authors_translation_table)
        pass

    def get_authors_from_line(self, line):
        authors = line.split(",")
        authors = authors[:-1]  # Delete the last empty string because of the trailing comma
        authors = frozenset(authors)
        return authors
    
    # assume that an author is not mentioned twice for the same article
    def build_authors_dict(self, authors):
        # TODO: defaultdict to throw away the use of if else
        for author in authors:
            if author not in self.authors_translation_table:
                index = len(self.authors_translation_table) + 1
                self.authors_translation_table[author] = index 
                self.authors_counts[index] = 1
            else:
                index = self.authors_translation_table.get(author)
                self.authors_counts[index] += 1


    def close_file(self):
        pass  # You can add code to close the file here if needed

# Example usage:
file_path = 'small-xmlparsed.txt'  # Replace with the path to your text file
translator = FirstPass(file_path)
translator.process_file()
print(translator.data)

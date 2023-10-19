from collections import defaultdict
from itertools import combinations
from firstpass import FirstPass

def find_frequent_author_groups(data, threshold):
    # Step 1: Initialize variables
    authors_counts = defaultdict(int)
    frequent_groups = {}  # To store frequent groups and their counts
    k = 1  # Initialize group size

    # Step 2: Count occurrences of individual authors
    for publication in data:
        for author in publication:
            authors_counts[author] += 1

    # Step 3: Generate frequent itemsets for larger group sizes
    while True:
        # Step 3a: Generate candidate itemsets of size k + 1
        candidate_groups = generate_candidate_groups(authors_counts, k)
        if not candidate_groups:
            break

        # Step 3b: Count occurrences of candidate itemsets in the dataset
        authors_counts = count_candidate_groups(data, candidate_groups)

        # Step 3c: Prune itemsets that do not meet the support threshold
        authors_counts, frequent_groups_k = prune_infrequent_groups(authors_counts, threshold)
        frequent_groups.update(frequent_groups_k)

        k += 1

    return frequent_groups


def generate_candidate_groups(authors_counts, k):
    """
    Optimized: Generate candidate groups of size k + 1 by joining frequent groups of size k.
    """
    authors = list(authors_counts)  # Convert to a list for indexing

    # Generate combinations of k-sized groups
    itertool = combinations(set(authors), k+1)
    candidates = []

    for group1, group2 in itertool:
        new_candidate = set(group1).union(group2)
        candidates.append(frozenset(new_candidate))

    return set(candidates)


def count_candidate_groups(data, candidate_groups):
    """
    Optimized: Count occurrences of candidate groups efficiently by scanning the dataset once.
    """
    authors_counts = defaultdict(int)
    for publication in data:
        publication_authors = set(publication)
        for group in candidate_groups:
            if group.issubset(publication_authors):
                authors_counts[group] += 1
    return authors_counts

def prune_infrequent_groups(authors_counts, threshold):
    """
    Optimized: Prune infrequent groups and return frequent groups along with the updated counts.
    """
    frequent_groups = {}
    new_authors_counts = defaultdict(int)
    for group, count in authors_counts.items():
        if count >= threshold:
            frequent_groups[group] = count
            new_authors_counts[group] = count
    return new_authors_counts, frequent_groups

# Example usage
file_path = 'small-xmlparsed.txt'  # Replace with the path to your text file
fp = FirstPass(file_path)
fp.process_file()

support_threshold = 2  # Adjust this threshold as needed
frequent_groups = find_frequent_author_groups(fp.data, support_threshold)
print(frequent_groups)

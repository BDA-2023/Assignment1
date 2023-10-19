from collections import defaultdict
from itertools import combinations

def find_frequent_author_groups(data, threshold):
    # Step 1: Initialize variables
    authors_counts = defaultdict(int)
    frequent_groups = {}  # To store frequent groups and their counts
    k = 1  # Initialize group size

    # Step 2: Count occurrences of individual authors
    for publication in data:
        for author in publication:
            authors_counts[frozenset([author])] += 1

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
    candidates = set()
    for group1 in authors_counts:
        for group2 in authors_counts:
            if len(group1.union(group2)) == k + 1:
                candidates.add(group1.union(group2))
    return candidates

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
data = [
    {"Author1", "Author2", "Author3"},
    {"Author2", "Author3", "Author4"},
    {"Author1", "Author2", "Author4"},
    {"Author2", "Author3", "Author4"},
]

threshold = 2  # Adjust this threshold as needed
frequent_groups = find_frequent_author_groups(data, threshold)
print(frequent_groups)

from collections import defaultdict
from itertools import combinations
from firstpass import FirstPass
import cProfile
import time


def find_frequent_author_groups(data, threshold):
    # Step 1: Initialize variables
    authors_counts = defaultdict(int)
    frequent_groups = {}  # To store frequent groups and their counts
    k = 1  # Initialize group size -> how many authors published together
    max_k = 7 # max paired authors in a group to search for

    # Step 2: Count occurrences of individual authors
    for publication in data:
        for author in publication:
            authors_counts[author] += 1

    candidate_groups = generate_candidate_groups(authors_counts, k)

    # Step 3: Generate frequent itemsets for larger group sizes
    while True:
        # Step 3a: Generate candidate itemsets of size k + 1
        t0 = time.time()
        if k > 1:
            candidate_groups = generate_candidate_groups_k(authors_counts, k)
        if not candidate_groups:
            break
        # Step 3b: Count occurrences of candidate itemsets in the dataset
        authors_counts = count_candidate_groups(data, candidate_groups)

        # # # Step 3c: Prune itemsets that do not meet the support threshold
        authors_counts, frequent_groups_k = prune_infrequent_groups(authors_counts, threshold)
        frequent_groups = frequent_groups_k

        t1 = time.time()
        total = t1-t0
        print(f"Time for k={k}: {total} seconds")
        k += 1
        if k==max_k:
            break

    return frequent_groups


def generate_candidate_groups_k(authors_counts, k):
    """
    Optimized: Generate candidate groups of size k + 1 by joining frequent groups of size k.
    """
    candidates = set()
    group_keys = list(authors_counts.keys())
    for i in range(len(group_keys)):
        group1 = group_keys[i]
        for j in range(i + 1, len(group_keys)):
            group2 = group_keys[j]
            new_candidate = frozenset(group1).union(group2)
            if len(new_candidate) == k + 1:
                candidates.add(new_candidate)
    return candidates


def generate_candidate_groups(authors_counts, k):
    """
    Optimized: Generate candidate groups of size k + 1 by joining frequent groups of size k.
    """
    authors = list(authors_counts)  # Convert to a list for indexing
    # Generate combinations of k-sized groups without them being duplicates (e.g., AB = BA)
    candidates = list(combinations(authors, k + 1))
    return set(candidates)


def count_candidate_groups(data, candidate_groups):
    """
    Optimized: Count occurrences of candidate groups efficiently by scanning the dataset once.
    """
    authors_counts = defaultdict(int)
    for publication in data:
        publication_authors = set(publication)
        for group in candidate_groups:
            if frozenset(group).issubset(publication_authors):
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

profile = cProfile.Profile()
profile.enable()
fp.process_file()
profile.disable()
profile.dump_stats("profile_FirstPass_med.prof")

support_threshold = 2  # threshold of how frequent a author needs to be at min.
profile.enable()
frequent_groups = find_frequent_author_groups(fp.data, support_threshold)
profile.disable()
profile.dump_stats("profile_SecondPass_k4s2_med.prof")
# frequent_groups = find_most_frequent_groups(fp.data)
# frequent_groups = find_frequent_author_groups(fp.data, support_threshold)
print(frequent_groups)


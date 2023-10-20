from collections import defaultdict
from itertools import combinations
from firstpass import FirstPass
import cProfile


def find_frequent_author_groups(data, threshold):
    # Step 1: Initialize variables
    authors_counts = defaultdict(int)
    frequent_groups = {}  # To store frequent groups and their counts
    k = 1  # Initialize group size -> how many authors published together
    max_k = 4 # max paired authors in a group to search for

    # Step 2: Count occurrences of individual authors
    for publication in data:
        for author in publication:
            authors_counts[author] += 1

    candidate_groups = generate_candidate_groups(authors_counts, k)

    # Step 3: Generate frequent itemsets for larger group sizes
    while True:
        # Step 3a: Generate candidate itemsets of size k + 1
        if k > 1:
            candidate_groups = generate_candidate_groups_k(authors_counts, k)
        if not candidate_groups:
            break
        # Step 3b: Count occurrences of candidate itemsets in the dataset
        authors_counts = count_candidate_groups(data, candidate_groups)

        # # # Step 3c: Prune itemsets that do not meet the support threshold
        authors_counts, frequent_groups_k = prune_infrequent_groups(authors_counts, threshold)
        frequent_groups = frequent_groups_k
        #TODO is authors_counts nodig -> kan je niet gewoon frequent_groups_k terug meegeven?

        k += 1
        if k==max_k:
            break


    return frequent_groups


def generate_candidate_groups_k(authors_counts, k):
    """
    Optimized: Generate candidate groups of size k + 1 by joining frequent groups of size k.
    """
    frequent_groups = [group for group, count in authors_counts.items() if len(group) == k]
    
    candidates = set()
    
    for i, group1 in enumerate(frequent_groups):
        for group2 in frequent_groups[i+1:]:
            new_candidate = frozenset(group1).union(group2)
            if len(new_candidate) == k + 1:
                candidates.add(new_candidate)
    
    return candidates

# def generate_candidate_groups(authors_counts, k):
#     """
#     Optimized: Generate candidate groups of size k + 1 by joining frequent groups of size k.
#     """
#     authors = list(authors_counts)  # Convert to a list for indexing

#     frequent_groups = set(frozenset({author}) for author in authors if authors_counts[author] >= k)

#     candidates = set()
    
#     for group1 in frequent_groups:
#         for group2 in frequent_groups:
#             if len(group1.union(group2)) == k + 1:
#                 new_candidate = frozenset(group1.union(group2))
#                 candidates.add(new_candidate)

#     return candidates

def generate_candidate_groups(authors_counts, k):
    """
    Optimized: Generate candidate groups of size k + 1 by joining frequent groups of size k.
    """
    authors = list(authors_counts)  # Convert to a list for indexing
    # Generate combinations of k-sized groups without them being duplicates (e.g., AB = BA)
    candidates = list(combinations(authors, k + 1))
    return set(candidates)

# def generate_candidate_groups(authors_counts, k):
#     """
#     Optimized: Generate candidate groups of size k + 1 by joining frequent groups of size k.
#     """
#     authors = list(authors_counts)  # Convert to a list for indexing

#     # Generate combinations of k-sized groups without them being duplicates AB = BA
#     itertool = combinations(set(authors), k+1)
#     candidates = []
    
#     for group1, group2 in itertool:
#         new_candidate = set(group1).union(group2)
#         print(new_candidate)
#         candidates.append(frozenset(new_candidate))

#     return set(candidates)


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
profile.dump_stats("profile_FirstPass.prof")

support_threshold = 2  # threshold of how frequent a author needs to be at min.
profile.enable()
frequent_groups = find_frequent_author_groups(fp.data, support_threshold)
profile.disable()
profile.dump_stats("profile_SecondPass_k4s2.prof")
print(frequent_groups)



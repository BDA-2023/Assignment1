import cProfile
from collections import defaultdict
import time
from firstpass import FirstPass
from itertools import combinations

def find_frequent_groups(data, min_support, max_group_size):
    # Generate candidate sets of size 1
    candidate_sets = [{author} for authors_from_article in data for author in authors_from_article]
    frequent_sets = []
    k = 1

    while candidate_sets:
        t0 = time.time()
        # Count the support for each candidate set
        item_counts = count_supports(data, candidate_sets)
        # Prune candidates with support below the minimum support threshold
        frequent_sets_k = [set(item) for item, count in item_counts.items() if count >= min_support]
        # Generate candidate sets of size k+1
        generate_candidate_sets(max_group_size, k, frequent_sets_k)

        frequent_sets.extend(frequent_sets_k)
        t1 = time.time()
        total = t1-t0
        print(f"Time for k={k}: {total} seconds")
        if k == max_group_size:
            break
        k += 1

    return frequent_sets

def generate_candidate_sets(max_group_size, k, frequent_sets_k):
    candidate_sets = []
    if k < max_group_size:
        for i in range(len(frequent_sets_k)):
            for j in range(i + 1, len(frequent_sets_k)):
                new_candidate = frequent_sets_k[i].union(frequent_sets_k[j])
                if len(new_candidate) == k + 1:
                    candidate_sets.append(new_candidate)

def count_supports(data, candidate_sets):
    item_counts = {}
    for authors_from_article in data:
        for candidate_set in candidate_sets:
            if set(candidate_set).issubset(authors_from_article):
                if tuple(candidate_set) in item_counts:
                    item_counts[tuple(candidate_set)] += 1
                else:
                    item_counts[tuple(candidate_set)] = 1
    return item_counts

min_support = 2  # Minimum support count for a group to be considered frequent
max_group_size = 10  # Maximum group size
min_group_size = 2  # Minimum group size

itemset_counts = defaultdict(int)
file_path = 'txt/small-xmlparsed.txt'  # Replace with the path to your text file
fp = FirstPass(file_path)
fp.process_file(itemset_counts,min_support, max_group_size)

profile = cProfile.Profile()
profile.enable()
frequent_groups = find_frequent_groups(fp.data, min_support, max_group_size)
profile.disable()
profile.dump_stats("profile_Versie2_full.prof")
print(f"Frequent Groups (Size {min_group_size}-{max_group_size}) with Support >= {min_support}:")
print(frequent_groups)
for group in frequent_groups:
    if len(group) <= max_group_size and len(group) >= min_group_size:
        print(group)

from collections import defaultdict
from itertools import combinations
from firstpass import FirstPass
import cProfile
import time
import argparse
import math

"""
TODO:
- should you count more than the support? kinda seems stupid
"""

def find_frequent_groups(data, itemset_counts, support_threshold = 2, max_k = 10):
    result_frequent_sets = []
    frequent_sets_k = [itemset for itemset, count in itemset_counts.items() if count >= support_threshold]
    itemset_counts = defaultdict(int)
    
    k = 1
    while True:
        if k >= max_k:
            break
        
        if print_time:
            t0 = time.time()
        # Count the support for each candidate set
        # print(f"frequent sets: {len(data)*len(frequent_sets_k)} \t({len(frequent_sets_k)}) \t- pow: {len(data)*pow(k,k)} \t(max {pow(k,k)}) - datalength:{len(data)}")
        data = count_supports(data, itemset_counts, frequent_sets_k, k)
        # Prune candidates with support below the minimum support threshold
        frequent_sets_k = [itemset for itemset, count in itemset_counts.items() if count >= support_threshold]
        itemset_counts = defaultdict(int)


        if print_time:
            t1 = time.time()
            total = t1-t0
            print(f"Time for k={k+1}: {total} seconds")
        if print_iterative:
            print(frequent_sets_k)
            #print(f"\tFrequent sets length: {len(frequent_sets_k)} - powerset: {pow(k,k)}")

        k += 1

        if len(frequent_sets_k) == 0:
            break

        result_frequent_sets.extend(frequent_sets_k)

    if print_output:
        print(result_frequent_sets)
    return result_frequent_sets

def count_supports(data, itemset_counts, frequent_sets_k, k):
    pruned_data = []
    for authors_from_article in data:
        if len(authors_from_article) < k+1:
            continue
        elif len(authors_from_article) == k+1:
            candidates_current_article = [frozenset(authors_from_article)]
        else: 
            candidates_current_article = generate_candidate_groups_pruned(authors_from_article, frequent_sets_k, k)

            
        pruned_data.append(authors_from_article)

        for candidate in candidates_current_article:
            itemset_counts[candidate] += 1
    # print(f"pruned data length: {len(pruned_data)}")
    return pruned_data

def generate_candidate_groups_pruned(authors_from_article, frequent_sets_k, k):
    """
    Optimized: Generate candidate groups of size k + 1 by joining frequent groups of size k that are only made from authors from current article.
    """
    if (k < 5):# math.comb(len(authors_from_article), k) < len(frequent_sets_k)):
        authors = list(authors_from_article)  # Convert to a list for indexing
        # Generate combinations of k-sized groups without them being duplicates (e.g., AB = BA)
        possible_candidates = list(combinations(authors, k))
        possible_candidates = frozenset([frozenset(x) for x in possible_candidates])

        pruned_frequent_sets = []
        for candidate_set in possible_candidates:
            if candidate_set in frequent_sets_k:
                pruned_frequent_sets.append(candidate_set)
    else:
        #print(f"{len(authors_from_article)*k} < {len(frequent_sets_k)}")
        pruned_frequent_sets = frequent_sets_k

    candidates = generate_candidate_groups(pruned_frequent_sets, k)

    return candidates

def generate_candidate_groups(frequent_sets_k, k):
    candidates = []
    for i in range(len(frequent_sets_k)):
        for j in range(i + 1, len(frequent_sets_k)):
            new_candidate = frequent_sets_k[i].union(frequent_sets_k[j])
            if len(new_candidate) == k + 1:
                candidates.append(new_candidate)
    return candidates

def parseArguments():
    parser = argparse.ArgumentParser(description="An a priori implementation for the dblp dataset")

    parser.add_argument("-s", "--support_threshold", type=int, default=2, help="The support threshold for this search")
    parser.add_argument("-k", "--max_k", type=int, default=10, help="The maximum group size supported by this search' execution")
    parser.add_argument("-pt", "--print_time", action="store_true", help="Print the time needed for every iteration k")
    parser.add_argument("-pi", "--print_iterative", action="store_true", help="Print the frequents every iteration k")
    parser.add_argument("-po", "--print_output", action="store_true", help="Print the final result")
    parser.add_argument("-f", "--file", type=str, default="1000.txt", help="The file which holds the authors for every article")
    parser.add_argument("-oc", "--optimized_candidates", action="store_true", help="Use the optimized version of candidates")
    parser.add_argument("-ma", "--max_articles", type=int, default=100000, help="The maximum number of articles read from the current file")


    args = parser.parse_args()
    global print_time, print_iterative, file_path, optimized_candidates, print_output
    print_time = args.print_time
    print_iterative = args.print_iterative
    file_path += args.file
    optimized_candidates = args.optimized_candidates
    print_output = args.print_output

    return args


print_time = False
print_iterative = False
optimized_candidates = False
print_output = False
file_path = 'txt/'

def main():
    args = parseArguments()
    fp = FirstPass(file_path)
    profile = cProfile.Profile()
    itemset_counts = defaultdict(int)

    profile.enable()
    fp.process_file(itemset_counts, args.max_articles)
    profile.disable()
    profile.dump_stats(f"profiles/profile_FirstPass_{args.max_articles}.prof")

    profile.enable()
    frequents = find_frequent_groups(fp.data, itemset_counts, args.support_threshold, args.max_k)
    profile.disable()
    profile.dump_stats(f"profiles/profile_FindFrequents_{args.file}_{args.max_articles}_k={args.max_k}_s={args.support_threshold}_k<5.prof")

if __name__ == "__main__":
    main()
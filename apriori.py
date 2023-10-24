from itertools import combinations
import pstats
from firstpass import FirstPass
import cProfile
import time
import argparse
import math
from customstream import init_custom_stream,write_log

"""
TODO:
- should you count more than the support? kinda seems stupid
"""

def find_frequent_groups(data, itemset_counts, support_threshold = 2, max_k = 10):
    result_frequent_sets = {}
    result_frequent_sets.update(itemset_counts)

    k = 1
    while True:
        if k >= max_k:
            break
        
        if print_time:
            t0 = time.time()
        # Count the support for each candidate set
        # print(f"frequent sets: {len(data)*len(frequent_sets_k)} \t({len(frequent_sets_k)}) \t- pow: {len(data)*pow(k,k)} \t(max {pow(k,k)}) - datalength:{len(data)}")
        data, itemset_counts = count_supports(data, itemset_counts, support_threshold, k)
        # Prune candidates with support below the minimum support threshold
        result_frequent_sets.update(itemset_counts)
        if len(itemset_counts) == 0:
            break
        k += 1

        if print_time:
            t1 = time.time()
            total = t1-t0
            print(f"Time for k={k+1}: {total} seconds")
        if print_iterative:
            print(itemset_counts)

    result_frequent_sets = list(filter(greater_equal_support_threshold, result_frequent_sets.items()))
    if print_output:
        print(result_frequent_sets)
    return result_frequent_sets

def greater_equal_support_threshold(key_value):
    global support_threshold
    return key_value[1] >= support_threshold

# def filter_itemset_counts(result_frequent_sets, itemset_counts):
#     filtered_itemset_counts = {}(filter(greater_equal_support_threshold, itemset_counts.items()))

#     result_frequent_sets.update(filtered_itemset_counts)
    

def count_supports(data, frequent_sets_unfiltered, support_threshold, k):
    pruned_data = []
    itemset_counts = {}
    print(f"frequent sets size: {len(frequent_sets_unfiltered)}")
    for authors_from_article in data:
        if len(authors_from_article) < k+1:
            continue
        # elif len(authors_from_article) == k+1:
        #     candidates_current_article = [frozenset(authors_from_article)]
        else: 
            candidates_current_article = generate_candidate_groups_with_combinations(authors_from_article, frequent_sets_unfiltered, support_threshold, k)
            pruned_data.append(authors_from_article)

        for candidate in candidates_current_article:
            if candidate in itemset_counts:
                itemset_counts[candidate] += 1
            else:
                itemset_counts[candidate] = 1
    # print(f"pruned data length: {len(pruned_data)}")
    return pruned_data, itemset_counts

def generate_candidate_groups_with_combinations(authors_from_article, frequent_sets_unfiltered, support_threshold, k):
    """
    Optimized: Generate candidate groups of size k + 1 by joining frequent groups of size k that are only made from authors from current article.
    """

    #print(len(possible_candidates))
    #print(f"possible cand len:{len(possible_candidates)}")

    #print(len(pruned_frequent_sets))
    #print('-------')

    if math.comb(len(authors_from_article), k) < len(frequent_sets_unfiltered):
        authors_list = list(authors_from_article)  # Convert to a list for indexing
        # Generate combinations of k-sized groups without them being duplicates (e.g., AB = BA)
        possible_candidates = list(combinations(authors_list, k))
        possible_candidates = frozenset([frozenset(x) for x in possible_candidates])
        pruned_frequent_sets = []
        for candidate_set in possible_candidates:
            if candidate_set in frequent_sets_unfiltered and frequent_sets_unfiltered[candidate_set] >= support_threshold:
                pruned_frequent_sets.append(candidate_set)
    else:
        pruned_frequent_sets = [key for key,_ in filter(greater_equal_support_threshold, frequent_sets_unfiltered.items())]
    #print(f"frequent set size {frequent_set_size}")
    candidates = generate_candidate_groups(pruned_frequent_sets, k)

    return candidates

def generate_candidate_groups(pruned_frequent_sets, k):
    frequent_set_size = len(pruned_frequent_sets)
    candidates = []
    for i in range(frequent_set_size):
        for j in range(i + 1, frequent_set_size):
            if len(pruned_frequent_sets[i]) > k+1 or len(pruned_frequent_sets[j]) > k+1:
                continue
            new_candidate = pruned_frequent_sets[i].union(pruned_frequent_sets[j])
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
    global print_time, print_iterative, file_path, optimized_candidates, print_output, support_threshold
    print_time = args.print_time
    print_iterative = args.print_iterative
    file_path += args.file
    optimized_candidates = args.optimized_candidates
    print_output = args.print_output
    support_threshold = args.support_threshold

    return args


print_time = False
print_iterative = False
optimized_candidates = False
print_output = False
file_path = 'txt/'
support_threshold = 2

def main():
    args = parseArguments()
    fp = FirstPass(file_path)
    profile = cProfile.Profile()
    itemset_counts = {}
    
    
    original_stdout,timestamp,custom_stream = init_custom_stream()

    profile.enable()
    fp.process_file(itemset_counts, args.support_threshold, args.max_k,  args.max_articles)
    profile.disable()
    profile.dump_stats(f"profiles/profile_FirstPass_{args.max_articles}.prof")

    profile.enable()
    frequents = find_frequent_groups(fp.data, itemset_counts, args.support_threshold, args.max_k)
    profile.disable()
    log_file_name = f"FindFrequents_{args.file}_{args.max_articles}_k={args.max_k}_s={args.support_threshold}-{timestamp}"
    profile.dump_stats(f"profiles/profile_{log_file_name}.prof")
    stats = pstats.Stats(f"profiles/profile_{log_file_name}.prof")
    stats.strip_dirs().sort_stats("cumulative").print_stats()

    write_log(original_stdout,timestamp,custom_stream, log_file_name)

if __name__ == "__main__":
    main()

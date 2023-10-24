from itertools import combinations
import pstats
from firstpass import FirstPass
import cProfile
import time
import argparse
import math
from customstream import init_custom_stream,write_log

"""
    This file contains an implementation of the second pass (aka main step) of the A-priori algorithm
"""

'''
    Identifies for every group size k its maximum frequency count together with a listing of example groups
    @param: data, the whole dataset
    @param: itemset_counts, the occurrences per unique author in the dataset
    @optional param: support_threshold, the minimum threshold for an group's occurence also known as "s" (default=2)
    @optional param: max_k, the maximum group size of authors also known as "k" (default=10)
'''
def find_frequent_groups(data, itemset_counts, support_threshold = 2, max_k = 10):
    result_frequent_sets = {}
    result_frequent_sets.update(itemset_counts)

    k = 1
    while True: # Loop every k group size until max_k is reached
        if k >= max_k:
            break
        
        if print_time:
            t0 = time.time()
        # Count the support for each candidate set
        data, itemset_counts = count_supports(data, itemset_counts, support_threshold, k)
        # Update the frequent author groups
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

    # Filter via greater_equal_support_threshold function (if true -> put in list)
    result_frequent_sets = list(filter(greater_equal_support_threshold, result_frequent_sets.items()))
    if print_output:
        print(result_frequent_sets)
    return result_frequent_sets

'''
    Function to filter out, if item is above the support threshold
    @param: key_value, the occurrence of a frequent author group
'''
def greater_equal_support_threshold(key_value):
    global support_threshold
    return key_value[1] >= support_threshold
    
'''
    Identifies for every group size k its maximum frequency count together with a listing of example groups
    @param: data, the whole dataset (can be pruned for efficiency)
    @param: frequent_sets_unfiltered, the occurrences per unique author in the dataset (can be pruned for efficiency)
    @param: support_threshold, the minimum threshold for an group's occurence also known as "s"
    @param: max_k, the maximum group size of authors also known as "k"
'''
def count_supports(data, frequent_sets_unfiltered, support_threshold, k):
    pruned_data = []
    itemset_counts = {}
    for authors_from_article in data:
        if len(authors_from_article) < k+1:
            continue
        else: 
            candidates_current_article = generate_candidate_groups_with_combinations(authors_from_article, frequent_sets_unfiltered, support_threshold, k)
            pruned_data.append(authors_from_article)

        for candidate in candidates_current_article:
            if candidate in itemset_counts:
                itemset_counts[candidate] += 1
            else:
                itemset_counts[candidate] = 1
    return pruned_data, itemset_counts # replace data with pruned data for this kth iteration

'''
    Optimized: Generate candidate groups of size k + 1 by joining frequent groups of size k that are only made from authors from current article
    @param: authors_from_article, current authors from an article
    @param: frequent_sets_unfiltered, the occurrences per unique author in the dataset (can be pruned for efficiency)
    @param: support_threshold, the minimum threshold for an group's occurence also known as "s"
    @param: max_k, the maximum group size of authors also known as "k"
'''
def generate_candidate_groups_with_combinations(authors_from_article, frequent_sets_unfiltered, support_threshold, k):

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
    candidates = generate_candidate_groups(pruned_frequent_sets, k)
    return candidates

'''
    Generate candidate groups of size k + 1 by joining frequent groups of size k
    @param: pruned_frequent_sets, current frequent author groups
    @param: max_k, the maximum group size of authors also known as "k"
'''
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

'''
    Parse commandline arguments
'''
def parseArguments():
    parser = argparse.ArgumentParser(description="An a priori implementation for the dblp dataset")

    parser.add_argument("-s", "--support_threshold", type=int, default=2, help="The support threshold for this search")
    parser.add_argument("-k", "--max_k", type=int, default=10, help="The maximum group size supported by this search' execution")
    parser.add_argument("-pt", "--print_time", action="store_true", help="Print the time needed for every iteration k")
    parser.add_argument("-pi", "--print_iterative", action="store_true", help="Print the frequents every iteration k")
    parser.add_argument("-po", "--print_output", action="store_true", help="Print the final result")
    parser.add_argument("-f", "--file", type=str, default="1000.txt", help="The file which holds the authors for every article")
    parser.add_argument("-ma", "--max_articles", type=int, default=100000, help="The maximum number of articles read from the current file")

    args = parser.parse_args()
    global print_time, print_iterative, file_path, print_output, support_threshold
    print_time = args.print_time
    print_iterative = args.print_iterative
    file_path += args.file
    #print_output = args.print_output
    support_threshold = args.support_threshold

    return args


print_time = False
print_iterative = False
print_output = True
file_path = 'txt/'
support_threshold = 2

'''
    Main
'''
def main():
    args = parseArguments()
    fp = FirstPass(file_path)
    profile = cProfile.Profile()
    itemset_counts = {}
    
    # Custom stdout logging
    original_stdout,timestamp,custom_stream = init_custom_stream()

    # Profile for debugging and timings per function (bottleneck searching)
    profile.enable()
    fp.process_file(itemset_counts, args.support_threshold, args.max_k,  args.max_articles)
    profile.disable()
    try:
        profile.dump_stats(f"profiles/profile_FirstPass_{args.max_articles}.prof")

        # Profile for debugging and timings per function (bottleneck searching)
        profile.enable()
        frequents = find_frequent_groups(fp.data, itemset_counts, args.support_threshold, args.max_k)
        profile.disable()

        log_file_name = f"FindFrequents_{args.file}_{args.max_articles}_k={args.max_k}_s={args.support_threshold}-{timestamp}"
        profile.dump_stats(f"profiles/profile_{log_file_name}.prof")

        # Show stats immediately
        stats = pstats.Stats(f"profiles/profile_{log_file_name}.prof")
        stats.strip_dirs().sort_stats("cumulative").print_stats()

        write_log(original_stdout,timestamp,custom_stream, log_file_name)
    except FileNotFoundError:
        print("directory logs/ or profiles/ does not exist so logging is disabled")


'''
    Script startpoint
'''
if __name__ == "__main__":
    main()

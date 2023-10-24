import cProfile
from collections import defaultdict
import time
from firstpass import FirstPass
import argparse
from customstream import init_custom_stream,write_log

"""
    This file contains an implementation of the PCY algorithm, this is not algorithm is not quite complete and does noet use bitmaps for memory efficiency
"""

# Some possible optimizations:
# - Throw away combinations that are less than support (dont keep looping complete data)
# - Optimizations used in A-priori

''' 
    Count authors in dataset
    @param: baskets, the whole dataset
    @param: itemsets, all the unique authors
'''
def count_itemsets(baskets, itemsets):
        counts = defaultdict(int)
        for basket in baskets:
            for itemset in itemsets:
                if set(itemset).issubset(basket):
                    counts[itemset] += 1
        return counts

''' 
    PCY algorithm implementation
    @param: dataset, the whole dataset
    @param: itemset_counts, all the unique authors and their respective occurences
    @param: min_support, the minimum threshold for an group's occurence also known as "s"
'''
def pcy_algorithm_k(dataset, itemset_counts, min_support):
    # First Pass: Count single items and create the hash table for k-groups
    item_counts = itemset_counts
    k_group_hash_table = defaultdict(int)
    k_group_hash_table = count_itemsets(dataset, itemset_counts)
    # Identify promising k-groups
    promising_k_groups = [group for group, count in k_group_hash_table.items() if count >= min_support]

    # Second Pass: Generate candidates and count frequent itemsets
    frequent_itemsets = set()  # Use a set to avoid duplicates

    # Loop over every k group and single author -> create pairs -> check if in dataset and count
    for group in promising_k_groups:
        for single_item, _ in item_counts.items(): # generate candidates
            if single_item not in group:
                candidate = tuple(sorted(list(set(group) | set(single_item))))

                # Check if the candidate itemset is in the dataset and not counted yet
                candidate_count = 0
                for basket in dataset:
                    if set(candidate).issubset(basket) and len(candidate) > 1:
                        candidate_count += 1

                if candidate_count >= min_support: # prune candidates via the threshold
                    frequent_itemsets.add((candidate, candidate_count))

    return list(frequent_itemsets)  # Convert the set to a list before returning


'''
    Parse commandline arguments
'''
def parseArguments():
    parser = argparse.ArgumentParser(description="An PCY implementation for the dblp dataset")

    parser.add_argument("-s", "--support_threshold", type=int, default=2, help="The support threshold for this search")
    parser.add_argument("-k", "--max_k", type=int, default=10, help="The maximum group size supported by this search' execution")
    parser.add_argument("-pt", "--print_time", action="store_true", help="Print the time needed for every iteration k")
    parser.add_argument("-po", "--print_output", action="store_true", help="Print the final result")
    parser.add_argument("-f", "--file", type=str, default="1000.txt", help="The file which holds the authors for every article")
    parser.add_argument("-ma", "--max_articles", type=int, default=100000, help="The maximum number of articles read from the current file")

    args = parser.parse_args()
    global print_time, file_path, print_output
    print_time = args.print_time
    file_path += args.file
    print_output = args.print_output

    return args

print_time = False
print_output = False
file_path = 'txt/'

'''
    Main
'''
def main():
    args = parseArguments()
    fp = FirstPass(file_path)
    profile = cProfile.Profile()
    itemset_counts = defaultdict(int)
    
    # Custom stdout logging
    original_stdout,timestamp,custom_stream = init_custom_stream()

    # Profile for debugging and timings per function (bottleneck searching)
    profile.enable()
    fp.process_file(itemset_counts, args.max_articles)
    profile.disable()
    profile.dump_stats(f"profiles/profile_PCYFirstPass_{args.max_articles}.prof")

    # Profile for debugging and timings per function (bottleneck searching)
    profile.enable()
    if print_time:
        t0 = time.time()
    frequents_pcy = pcy_algorithm_k(fp.data, itemset_counts, args.support_threshold) # PCY
    if print_time:
        t1 = time.time()
        total = t1-t0
    profile.disable()
    log_file_name = f"PCY_{args.file}_{args.max_articles}_k={args.max_k}_s={args.support_threshold}"
    profile.dump_stats(f"profiles/profile_{log_file_name}.prof")

    if print_output:
        for itemset in frequents_pcy:
            print(f"Itemset: {itemset}")
    if print_time:
        print(f"Execution duration: {total} seconds")

    write_log(original_stdout,timestamp,custom_stream, log_file_name)

'''
    Script startpoint
'''
if __name__ == "__main__":
    main()

import cProfile
from collections import defaultdict
import time
from firstpass import FirstPass
from itertools import combinations
import argparse
from customstream import init_custom_stream,write_log

# TODO throw away combinations that are less than support (dont keep looping complete data)
# TODO check in create_baskets if a unique combination already exists

def count_itemsets(baskets, itemsets): # Versie 1 ~ 2 seconden (k=2,s=7)
        counts = defaultdict(int)
        for basket in baskets:
            for itemset in itemsets:
                if set(itemset).issubset(basket):
                    counts[itemset] += 1
        return counts

# Pre: no duplicates
# def create_baskets(dataset, item_counts,k_group_hash_table,k, min_support): # versie 2 ~0.8 sec (k=2,s=7)
#     unique_items = defaultdict(int)
#     # for basket in dataset:

#     for single_item, count in item_counts.items():
#         if count >= min_support:
#             unique_items[single_item] = count
#     # print(unique_items)
#     if len(unique_items) >= k:
#         # Extract items from the frozensets
#         items = [list(frozenset)[0] for frozenset in unique_items.keys()]
#         # Generate all (k-1) combinations from items
#         combinations_k_minus_1 = list(combinations(items,k))

#     unique_items_count = defaultdict(int)
#     for basket in dataset:
#         for item in combinations_k_minus_1:
#             if set(item).issubset(basket):
#                 unique_items_count[item] += 1
#     print([item for item,count in unique_items_count.items() if count >= min_support])

#     return item_counts,combinations_k_minus_1


def pcy_algorithm_k(dataset, itemset_counts, min_support, k):
    # First Pass: Count single items and create the hash table for k-groups
    item_counts = itemset_counts
    k_group_hash_table = defaultdict(int)
    k_group_hash_table = count_itemsets(dataset, itemset_counts)#create_baskets(dataset,item_counts,k_group_hash_table,k,min_support)
    # Identify promising k-groups
    promising_k_groups = [group for group, count in k_group_hash_table.items() if count >= min_support]

    # Second Pass: Generate candidates and count frequent itemsets
    frequent_itemsets = set()  # Use a set to avoid duplicates

    for group in promising_k_groups:
        for single_item, count in item_counts.items():
            if single_item not in group:
                candidate = tuple(sorted(list(set(group) | set(single_item))))

                # Check if the candidate itemset is in the dataset and not counted yet
                candidate_count = 0
                for basket in dataset:
                    if set(candidate).issubset(basket) and len(candidate) > 1:
                        candidate_count += 1

                if candidate_count >= min_support:
                    frequent_itemsets.add((candidate, candidate_count))

    return list(frequent_itemsets)  # Convert the set to a list before returning

def pcy_algorithm(dataset, min_support):
    # First Pass: Count single items and create the hash table for pairs
    single_item_counts = defaultdict(int)
    pair_hash_table = defaultdict(int)

    for basket in dataset:
        single_items = set(basket)

        for item in single_items:
            single_item_counts[item] += 1

        # Create pairs from the basket and update the hash table
        pairs = list(combinations(single_items, 2))
        for pair in pairs:
            pair_hash_table[pair] += 1

    # Identify promising pairs
    promising_pairs = [pair for pair, count in pair_hash_table.items() if count >= min_support]

    # Second Pass: Generate candidates and count frequent itemsets
    frequent_itemsets = []

    for pair in promising_pairs:
        item1, item2 = pair
        for single_item, count in single_item_counts.items():
            if single_item != item1 and single_item != item2:
                candidate = tuple(sorted([item1, item2, single_item]))

                # Check if the candidate itemset is in the dataset and not counted yet
                candidate_count = 0
                for basket in dataset:
                    if set(candidate).issubset(basket):
                        candidate_count += 1

                if candidate_count >= min_support:
                    frequent_itemsets.append((candidate, candidate_count))

    return frequent_itemsets



def parseArguments():
    parser = argparse.ArgumentParser(description="An PCY implementation for the dblp dataset")

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
    
    original_stdout,timestamp,custom_stream = init_custom_stream()

    profile.enable()
    fp.process_file(itemset_counts, args.max_articles)
    profile.disable()
    profile.dump_stats(f"profiles/profile_PCYFirstPass_{args.max_articles}.prof")

    profile.enable()
    if print_time:
        t0 = time.time()
    frequents_pcy = pcy_algorithm_k(fp.data, itemset_counts, args.support_threshold, args.max_k)
    if print_time:
        t1 = time.time()
        total = t1-t0
    profile.disable()
    log_file_name = f"PCY_{args.file}_{args.max_articles}_k={args.max_k}_s={args.support_threshold}"
    profile.dump_stats(f"profiles/profile_{log_file_name}.prof")

    if print_output:
        for itemset, count in frequents_pcy:
            print(f"Itemset: {itemset}, Count: {count}")
    if print_time:
        print(f"Execution duration: {total} seconds")

    write_log(original_stdout,timestamp,custom_stream, log_file_name)




if __name__ == "__main__":
    main()
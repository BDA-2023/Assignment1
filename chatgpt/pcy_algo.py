import cProfile
from collections import defaultdict
from firstpass import FirstPass
from itertools import combinations

def pcy_algorithm_k(dataset, min_support, k):
    # First Pass: Count single items and create the hash table for k-groups
    item_counts = defaultdict(int)
    k_group_hash_table = defaultdict(int)

    for basket in dataset:
        items = set(basket)

        for item in items:
            item_counts[item] += 1

        # Create k-groups from the basket and update the hash table
        k_groups = list(combinations(items, k))
        for group in k_groups:
            k_group_hash_table[group] += 1

    # Identify promising k-groups
    promising_k_groups = [group for group, count in k_group_hash_table.items() if count >= min_support]

    # Second Pass: Generate candidates and count frequent itemsets
    frequent_itemsets = []

    for group in promising_k_groups:
        for single_item, count in item_counts.items():
            if single_item not in group:
                candidate = tuple(sorted(list(group) + [single_item]))

                # Check if the candidate itemset is in the dataset and not counted yet
                candidate_count = 0
                for basket in dataset:
                    if set(candidate).issubset(basket):
                        candidate_count += 1

                if candidate_count >= min_support:
                    frequent_itemsets.append((candidate, candidate_count))

    return frequent_itemsets

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


file_path = 'small-xmlparsed.txt'  # Replace with the path to your text file
fp = FirstPass(file_path)
fp.process_file()
min_support = 2
k = 5
profile = cProfile.Profile()
profile.enable()
result = pcy_algorithm_k(fp.data, min_support,k)
profile.disable()
# profile.dump_stats("profile_PCY_small.prof")
for itemset, count in result:
    print(f"Itemset: {itemset}, Count: {count}")

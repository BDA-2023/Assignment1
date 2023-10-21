# Analyze results
import pstats
# Load the profiling results
# stats = pstats.Stats("profile_FirstPass_supersmall.prof")
# # Sort the results by cumulative time (you can choose other sorting options)
# stats.strip_dirs().sort_stats("cumulative").print_stats()

stats = pstats.Stats("profiles/profile_FirstPass_10000.prof")
# Sort the results by cumulative time (you can choose other sorting options)
stats.strip_dirs().sort_stats("cumulative").print_stats()

for i in range(5, 8):
    stats = pstats.Stats(f"profiles/profile_FindFrequents_10000_k<{i}.prof")
    # Sort the results by cumulative time (you can choose other sorting options)
    print(f"k<{i}:")
    stats.strip_dirs().sort_stats("cumulative").print_stats()

stats = pstats.Stats("profiles/profile_FindFrequents_20000_k<6.prof")
# Sort the results by cumulative time (you can choose other sorting options)
stats.strip_dirs().sort_stats("cumulative").print_stats()

stats = pstats.Stats("profiles/profile_FindFrequents_100000.txt_100000_k=100_s=10_k<5.prof")
# Sort the results by cumulative time (you can choose other sorting options)
stats.strip_dirs().sort_stats("cumulative").print_stats()

stats = pstats.Stats("profiles/profile_FindFrequents_6milion.txt_7000000_k=300_s=250_k<5.prof")
# Sort the results by cumulative time (you can choose other sorting options)
stats.strip_dirs().sort_stats("cumulative").print_stats()
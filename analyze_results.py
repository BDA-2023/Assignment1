# Analyze results
import pstats
# Load the profiling results
# stats = pstats.Stats("profile_FirstPass_supersmall.prof")
# # Sort the results by cumulative time (you can choose other sorting options)
# stats.strip_dirs().sort_stats("cumulative").print_stats()

stats = pstats.Stats("profile_SuperFast_small.prof")
# Sort the results by cumulative time (you can choose other sorting options)
stats.strip_dirs().sort_stats("cumulative").print_stats()
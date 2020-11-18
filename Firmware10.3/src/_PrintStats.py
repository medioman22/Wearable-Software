# -*- coding: utf-8 -*-
import pstats
p = pstats.Stats('../Logs/stats.log')
p.strip_dirs().sort_stats(-1)

# Sort by name
# p.sort_stats('name')

# Sort by comulative calls
# p.sort_stats('cumulative').print_stats(10)

# Sort by time
# p.sort_stats('time').print_stats(10)

# Print the last stats
p.print_stats()

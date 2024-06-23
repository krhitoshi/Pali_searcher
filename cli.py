#!/usr/bin/env python3

import sys
import os
from pali_searcher import PaliSearcher, PaliSearcherMode

# keyword = "gahapatiputto"
# keyword = "jātovarake"
keyword = sys.argv[1]

target_text_groups = ["Vin", "DN", "MN", "SN", "AN",
                      "Khp", "Dhp", "Ud", "It", "Sn", "Pv", "Vm", "Th", "Thi", "J", "Nidd_I", "Nidd_II",
                      "Patis", "Ap", "Bv", "Cp",
                      "Dhs", "Vibh", "Dhatuk", "Pugg", "Kv", "Yam",
                      "Mil", "Vism", "Sp", "Ja"]

app_dir = os.path.abspath(os.path.dirname(__file__))
static_path = os.path.join(app_dir, "static")
searcher = PaliSearcher(static_path, mode=PaliSearcherMode.CLI)
results = searcher.search(target_text_groups, keyword)

for result in results:
      print("{}: {}".format(result.reference_info(), result.sentence))

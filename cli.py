#!/usr/bin/env python3

import sys
import re
from Pali_searcher import search_keyword

# keyword = "gahapatiputto"
# keyword = "jātovarake"
keyword = sys.argv[1]

try:
    re.compile(keyword)
except Exception:
    print("Regex Error!", file=sys.stderr)
    sys.exit(1)

text_list = ["Vin_I", "Vin_II", "Vin_III", "Vin_IV", "Vin_V",
    "DN_I", "DN_II", "DN_III",
    "MN_I", "MN_II", "MN_III",
    "SN_I", "SN_II", "SN_III", "SN_IV", "SN_V",
    "AN_I", "AN_II", "AN_III", "AN_IV", "AN_V",
    "Khp", "Dhp", "Ud", "It", "Sn", "Pv", "Vm", "Th", "Thi", "J", "Nidd_I", "Nidd_II", "Paṭis_I", "Paṭis_II", "Ap", "Bv", "Cp",
    "Dhs", "Vibh", "Dhātuk", "Pugg", "Kv", "Yam_I", "Yam_II", "Mil", "Vism", "Sp", "Ja_1", "Ja_2", "Ja_3", "Ja_4", "Ja_5", "Ja_6"]

results = []

for text_type in text_list:
    results += search_keyword(text_type, keyword)

for result in results:
      print("{} :{}".format(result.name, result.text))

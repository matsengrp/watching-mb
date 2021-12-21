import json

json_path = "config.json"

with open(json_path) as json_file:
    json_decoded = json.load(json_file)

with open("../iqtree/ds.fasta.treefile") as tree_file:
    tree_string = tree_file.readline().rstrip()

json_decoded["starttree"] = tree_string

with open(json_path, "w") as json_file:
    json.dump(json_decoded, json_file, indent=4)
    json_file.write("\n")

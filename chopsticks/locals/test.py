import csv
import json

table = {}
PATH = "table.csv"
with open(PATH) as f:
	freader = csv.reader(f)
	first=True
	for row in freader:
		if first:
			first=False
		else:
			table[row[1]]=row[0]

with open('table.json', 'w') as outfile:
    json.dump(table, outfile, indent=4)

print(table)


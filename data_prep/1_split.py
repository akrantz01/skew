import csv
import multiprocessing
import os

SEGMENTS = multiprocessing.cpu_count()

os.mkdir("segments")

tabbed = open("newsArticlesWithLabels.tsv", "r")
comma_segments = [open(f"segments/segment-{i}.csv", "w") for i in range(SEGMENTS)]

reader = csv.reader(tabbed, delimiter="\t")
writers = [csv.writer(comma, delimiter=",") for comma in comma_segments]

for i, row in enumerate(reader):
    del row[1], row[1]

    writers[i % 16].writerow(row)

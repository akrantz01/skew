import csv
import multiprocessing

SEGMENTS = multiprocessing.cpu_count()

files = [open(f"downloaded/segment-{i}.csv", "r") for i in range(SEGMENTS)]
output = open("newsArticlesWithLabels.csv", "w")

readers = [csv.reader(file) for file in files]
writer = csv.writer(output)

for reader in readers:
    for row in reader:
        writer.writerow(row)

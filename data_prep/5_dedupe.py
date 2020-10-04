import csv

original = csv.reader(open("processed-news-articles.csv", "r"))
final = csv.writer(open("final-data.csv", "w"))

rows = [row for row in original]
deduped_text_only = []
deduped = []

for row in rows:
    if row[0] not in deduped_text_only:
        deduped_text_only.append(row[0])
        deduped.append(row)

final.writerows(deduped)

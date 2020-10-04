import csv
from newspaper import Article, ArticleException
import os
from progress.bar import Bar
import sys

for d in ["downloaded", "logs", "failed"]:
    os.makedirs(d, exist_ok=True)

name = sys.argv[1]

lines = sum(1 for line in open(f"segments/{name}"))
progress = Bar("Downloading...", max=lines, suffix="%(percent).2f%% - %(eta)ds")

log_file = open(f"logs/{name}.log", "a")
failed_file = open(f"failed/{name}", "a")
in_file = open(f"segments/{name}", "r")
out_file = open(f"downloaded/{name}", "w")

reader = csv.reader(in_file)
writer = csv.writer(out_file)
failed_writer = csv.writer(failed_file)

log_file.write("New instance started...\n")

for row in reader:
    if row[0] == "url":
        progress.next()
        continue

    try:
        article = Article(row[0])
        article.download()
        article.parse()

        if article.text is None:
            log_file.write(f"{row[0]} - no article text found\n")
            failed_writer.writerow(row)
            progress.next()
            continue

        row[0] = article.text
    except ArticleException as e:
        log_file.write(f"{e}\n")
        failed_writer.writerow(row)
        progress.next()
        continue

    writer.writerow(row)
    progress.next()

in_file.close()
out_file.close()

progress.finish()

import csv

VOTE_MAPPING = {
    "Positive": 2,
    "SomewhatPositive": 1,
    "Neutral": 0,
    "SomewhatNegative": -1,
    "Negative": -2
}
DIFFERENCE_MAPPING = {
    4: ("extreme", "left"),
    3: ("strong", "left"),
    2: ("moderate", "left"),
    1: ("minimal", "left"),
    0: ("none", "neutral"),
    -1: ("minimal", "right"),
    -2: ("moderate", "right"),
    -3: ("strong", "right"),
    -4: ("extreme", "right")
}

original = open("newsArticlesWithLabels.csv", "r")
modified = open("processed-news-articles.csv", "w")

reader = csv.reader(original)
writer = csv.writer(modified)

for row in reader:
    [_, _, _, democrat, republican] = row

    democrat_mapped = VOTE_MAPPING[democrat]
    republican_mapped = VOTE_MAPPING[republican]

    extent, bias = DIFFERENCE_MAPPING[democrat_mapped - republican_mapped]

    writer.writerow([row[0], bias, extent])

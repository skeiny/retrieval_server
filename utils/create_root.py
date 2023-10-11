import csv
import os


def createRoot():
    with open('../input/jclist.csv', mode='r', encoding='utf-8') as file:
        csv_reader = csv.reader(file)

        # 跳过标题行
        next(csv_reader, None)

        for row in csv_reader:
            print(row)
            category, link, name, area, rank = row
            # if "journal".__eq__(str(category)):
            #     getJournal(link, name)
            # else:
            #     getConference(link, name)
            os.makedirs("../retrieval_root/" + area + "/" + rank + "/" + name, exist_ok=True)


if __name__ == '__main__':
    createRoot()


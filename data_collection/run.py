from collect import *
import csv


if __name__ == '__main__':
    with open('../input/todo.csv', mode='r', encoding='utf-8') as file:
        csv_reader = csv.reader(file)

        # 跳过标题行
        next(csv_reader, None)

        for row in csv_reader:
            print(row)
            category, link, name, area, rank = row
            if "journal".__eq__(str(category)):
                getJournal(link, name, area, rank)
            else:
                getConference(link, name, area, rank)

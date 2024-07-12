import csv
import re


def separate_by_commas(file_name):
    file_path = f'raw_data/{file_name}'
    with open(file_path) as csvfile:
        data = []
        csvreader = csv.reader(csvfile, delimiter='\t')
        for row in csvreader:
            line = re.sub("\s+", ",", row[0].strip())
            line_items = line.split(',')
            data.append(line_items)

    new_file_path = f'data_sets/{file_name}'
    with open(new_file_path, 'w') as newfile:
        csvwriter = csv.writer(newfile, delimiter=',',
                               quoting=csv.QUOTE_NONE)
        csvwriter.writerows(data)


separate_by_commas('rc104.csv')

import csv


def save_result(path, headers, results):
    f = open(path, 'w', newline='')
    f_csv = csv.writer(f)
    f_csv.writerow(headers)
    f_csv.writerows(results)

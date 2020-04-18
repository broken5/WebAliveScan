import csv


def save_result(path, headers, result):
    f = open(path, 'a+', newline='')
    f_csv = csv.writer(f)
    if headers:
        f_csv.writerow(headers)
    elif result:
        f_csv.writerow(result)

from lib.common.output import Output


def save_result(path, headers, results):
    data = ','.join(headers)
    data += '\n'
    for i in results:
        line = ''
        for h in headers:
            line += '"'+str(i[h]).replace('"', '""')+'",'
        data += line.strip(',') + '\n'
    try:
        with open(path, 'w', errors='ignore', newline='') as file:
            file.write(data)
            return True
    except TypeError:
        with open(path, 'wb') as file:
            file.write(data.encode())
            return True
    except Exception as e:
        Output().error(e.args)
        return False

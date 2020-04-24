import pathlib

default_ports = {80}  # 默认使用
small_ports = {80, 443, 8000, 8080, 8443}
medium_ports = {80, 81, 443, 591, 2082, 2087, 2095, 2096, 3000, 8000, 8001,
                8008, 8080, 8083, 8443, 8834, 8888}
large_ports = {80, 81, 300, 443, 591, 593, 832, 888, 981, 1010, 1311, 2082,
               2087, 2095, 2096, 2480, 3000, 3128, 3333, 4243, 4567, 4711,
               4712, 4993, 5000, 5104, 5108, 5800, 6543, 7000, 7396, 7474,
               8000, 8001, 8008, 8014, 8042, 8069, 8080, 8081, 8088, 8090,
               8091, 8016, 8118, 8123, 8172, 8222, 8243, 8280, 8281, 8333,
               8443, 8500, 8834, 8880, 8888, 8983, 9000, 9043, 9060, 9080,
               9090, 9091, 9200, 9443, 9800, 9981, 12443, 16080, 18091, 18092,
               20720, 28017}  # 可以在这里面添加端口
ports = {'default': default_ports, 'small': small_ports,
         'medium': medium_ports, 'large': large_ports}

# 忽略状态码配置
ignore_status_code = [400]
# SSL配置
verify_ssl = False
# 重定向配置
allow_redirects = True
# 扫描线程
threads = 1024
# 延迟配置
timeout = 3
realpath = pathlib.Path(__file__).parent
result_save_path = realpath.joinpath('results')

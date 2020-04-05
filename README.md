# WebAliveScan
安装
```
pip3 install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
```

使用帮助：
```
python3 webscan.py --target target.txt --port 80
python3 webscan.py --target target.txt --port large
```

config.py
```
# 可以指定需要忽略HTTP状态码
ignore_status_code = [400]

# 指定线程数量
threads = 1024
```


# WebAliveScan
安装
```
pip3 install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
```

使用帮助：
```
python3 webscan.py --help
INFO: Showing help with the command 'webscan.py -- --help'.

NAME
    webscan.py - Broken5

SYNOPSIS
    webscan.py FILE PORT

DESCRIPTION
    Example:
        python3 webscan.py --file=test.txt --port=80,443,8080,8989
        python3 webscan.py --file=test.txt --port=default
        python3 webscan.py --file=test.txt --port=large

POSITIONAL ARGUMENTS
    FILE
        域名文件路径
    PORT
        请求端口类型(default、small、medium，large)

NOTES
    You can also use flags syntax for POSITIONAL ARGUMENTS
```

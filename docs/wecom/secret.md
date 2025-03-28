# 配置企业微信密钥文件

[TOC]

## config文件配置

```shell
cd release && vim protocol/xwork/config.py
```

```shell
"""
Xwork configurations.
"""

CORPID = "必填"   # 企业微信所属企业ID
FWID = ""
SERVICE_ID = ""
SECRET = "必填"   # 企业微信专属密钥
TOKEN = "必填"    # 企业微信应用自定义Token
AES_KEY = "必填"  # 企业微信应用自定义 aes
```

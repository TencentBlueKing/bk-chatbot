# 配置Slack密钥文件

[TOC]

## config文件配置

```shell
cd release && vim protocol/slack/config.py
```

```shell
"""
Slack configurations.
"""

OAUTH_TOKEN = ""               # Bot User OAuth Token
SIGNING_SECRET = ""            # Slack signs the requests we send you using this secret. Confirm that each request comes from Slack by verifying its unique signature.
VERIFICATION_TOKEN = ""        # This deprecated Verification Token can still be used to verify that requests come from Slack, but we strongly recommend using the above, more secure, signing secret instead.

# this config used to add slack <-> bk
USER_WHITE_MAP = {
    "slack_account": "bk_username"
}
```

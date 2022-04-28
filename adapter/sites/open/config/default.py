# -*- coding: utf-8 -*-
import os

# sdk
ESB_SDK_NAME = "adapter.sites.open.blueking.component"

# bk_login
OAUTH_COOKIES_PARAMS = {"bk_token": "bk_token"}
RUN_VER_DISPLAY = os.environ.get("RUN_VER_DISPLAY", "企业版")
INIT_SUPERUSER = ["admin"]

BIZ_ACCESS_URL = os.getenv("BKAPP_BIZ_ACCESS_URL", "")
DEMO_BIZ_ID = os.getenv("BKAPP_DEMO_BIZ_ID", "")
DEMO_BIZ_EDIT_ENABLED = bool(os.getenv("BKAPP_DEMO_BIZ_EDIT_ENABLED", ""))

# footer 配置
FOOTER_CONFIG = {
    "footer": [
        {
            "zh": [
                {
                    "text": "QQ咨询(800802001)",
                    "link": "http://wpa.b.qq.com/cgi/wpa.php?ln=1&key=XzgwMDgwMjAwMV80NDMwOTZfODAwODAyMDAxXzJf",
                },
                {"text": "蓝鲸论坛", "link": "https://bk.tencent.com/s-mart/community"},
                {"text": "蓝鲸官网", "link": "https://bk.tencent.com/"},
                {"text": "蓝鲸智云桌面", "link": ""},
            ],
            "en": [
                {
                    "text": "QQ(800802001)",
                    "link": "http://wpa.b.qq.com/cgi/wpa.php?ln=1&key=XzgwMDgwMjAwMV80NDMwOTZfODAwODAyMDAxXzJf",
                },
                {"text": "BlueKing Forum", "link": "https://bk.tencent.com/s-mart/community"},
                {"text": "Blueking Official", "link": "https://bk.tencent.com/"},
                {"text": "BlueKing Desktop", "link": ""},
            ],
        }
    ],
    "copyright": "Copyright © 2012-2020 Tencent BlueKing. All Rights Reserved.",
}

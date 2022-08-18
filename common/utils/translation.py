"""
TencentBlueKing is pleased to support the open source community by making
蓝鲸智云PaaS平台社区版 (BlueKing PaaSCommunity Edition) available.
Copyright (C) 2017-2018 THL A29 Limited,
a Tencent company. All rights reserved.
Licensed under the MIT License (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
import os
import logging
import json
from tencentcloud.common import credential

from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.tmt.v20180321 import tmt_client, models

TencentCloudSecretId = os.getenv("TencentCloudSecretId", "")
TencentCloudSecretKey = os.getenv("TencentCloudSecretKey", "")

logger = logging.getLogger("root")


def translate_text(source_text, target_type, source_type="zh"):
    try:
        cred = credential.Credential(TencentCloudSecretId, TencentCloudSecretKey)
        client = tmt_client.TmtClient(cred, "ap-beijing")
        req = models.TextTranslateRequest()
        params = {"SourceText": source_text, "Source": source_type, "Target": target_type, "ProjectId": 0}
        req.from_json_string(json.dumps(params))
        resp = client.TextTranslate(req)
        result = json.loads(resp.to_json_string())
        return True, result["TargetText"]
    except TencentCloudSDKException as err:
        logger.exception(err)
        return False, repr(err)
    except Exception as _err:
        logger.exception(_err)
        return False, repr(_err)

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

import json
from urllib import parse
from typing import Union, Dict

from slack_sdk.signature import SignatureVerifier

from opsbot.log import logger


class Decryption:
    """
    Decrypt
    Parse
    Classify: Event text
    """
    def __init__(self, signing_secret: str, data: Union[str, bytes], headers: Dict):
        self.data = data
        self.headers = headers
        self.verifier = SignatureVerifier(signing_secret=signing_secret)

    def _decrypt(self):
        pass

    def is_valid(self) -> bool:
        return self.verifier.is_valid_request(self.data, self.headers)

    def parse(self) -> Dict:
        """
        :return:
        {
            payload
            interactive_message
        }
        """
        try:
            data = parse.unquote(self.data.decode())
            payload = data.split('=')[1]
            return json.loads(payload)
        except IndexError:
            data = self.data.decode()
            return json.loads(data)
        except (TypeError, json.JSONDecodeError) as e:
            logger.error(f'event data parse error: {str(e)}')
            return None

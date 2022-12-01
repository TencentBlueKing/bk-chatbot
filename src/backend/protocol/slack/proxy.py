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

from typing import (
    Any, Optional, Dict, Union, List
)

from quart import request, abort, jsonify

from opsbot.log import logger
from opsbot.proxy import (
    Api as BaseApi, Proxy as BaseProxy, UnifiedApi, _deco_maker,
    ActionFailed, ApiNotAvailable, HttpFailed, NetworkError
)
from .message import Message


class Proxy(BaseProxy):
    def __init__(self, api_root: Optional[str], api_config: Dict):
        super().__init__(message_class=Message,
                         api_class=UnifiedApi(http_api=HttpApi(api_root, api_config)))
        self._server_app.register_error_handler(Exception, self._handle_bad_request)

    on_text = _deco_maker('text')

    @classmethod
    async def _handle_url_verify(cls):
        payload = await request.json
        logger.info(payload)
        return jsonify({'challenge': payload['challenge']})

    @classmethod
    async def _handle_bad_request(cls, e: Exception):
        return jsonify(error='bad request', code=405)

    async def _handle_http(self):
        return await self._handle_url_verify()

    def run(self, host=None, port=None, *args, **kwargs):
        self._server_app.run(host=host, port=port, *args, **kwargs)

    async def send(self, context: Dict[str, Any],
                   message: Union[str, Dict[str, Any], List[Dict[str, Any]]],
                   **kwargs):
        pass


class HttpApi(BaseApi):
    def __init__(self, api_root: Optional[str], api_config: Dict, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._api_config = api_config
        self._api_root = api_root.rstrip('/') if api_root else None

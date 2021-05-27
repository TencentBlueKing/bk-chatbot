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
import abc

from typing import Any, Optional, Dict


class Api:
    """
    Api interface
    """
    __slots__ = ('api_name', )

    def __init__(self,
                 api_name: Optional[str],
                 api_root: Optional[str],
                 *args,
                 **kwargs):
        self.api_name = api_name
        self._api_root = api_root.rstrip('/') if api_root else None

    @abc.abstractmethod
    def _get_access_token(self) -> Optional[Dict[str, Any]]:
        """
        Get access_token
        """
        pass

    @abc.abstractmethod
    def _is_token_available(self) -> bool:
        """
        Judge the access_token available
        -time
        -filed
        """
        pass

    @abc.abstractmethod
    def _handle_api_result(result: Optional[Dict[str, Any]]) -> Any:
        """
        Deal response's result
        """
        pass

    @abc.abstractmethod
    async def call_action(self, action: str, **params) -> Optional[Dict[str, Any]]:
        """
        Send API request to call the specified action.
        """
        pass

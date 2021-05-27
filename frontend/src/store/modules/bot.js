/**
 * TencentBlueKing is pleased to support the open source community by making
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
 * @file app store
 * @author
 */

import http from '@/api'
// import queryString from 'query-string'

export default {
    namespaced: true,
    state: {
    },
    mutations: {
    },
    actions: {
        // 如果需要 mock，那么只需要在 url 后加上 AJAX_MOCK_PARAM 的参数，
        // 参数值为 mock/ajax 下的路径和文件名，然后加上 invoke 参数，参数值为 AJAX_MOCK_PARAM 参数指向的文件里的方法名
        // 例如本例子里，ajax 地址为 table_data，mock 地址为 table_data?AJAX_MOCK_PARAM=index&invoke=getTableData

        /**
         * enterExample1 请求，get 请求
         *
         * @param {Object} context store 上下文对象 { commit, state, dispatch }
         * @param {Object} params 请求参数
         *
         * @return {Promise} promise 对象
         */

        getBotTableData (context, params, config = {}) {
            // 后续为多机器人环境预留
            // const mockUrl = `${AJAX_URL_PREFIX}/api/v1/` + params.bizId + `/bot/?${AJAX_MOCK_PARAM}=intent&invoke=botList&${queryString.stringify(params.data)}`
            // return http.get(mockUrl, params, config)
            return {
                'result': true,
                'code': '200',
                'message': 'success',
                'data': {
                    'count': 1,
                    'next': '',
                    'previous': null,
                    'results': [
                        {
                            'id': -1,
                            'biz_id': '',
                            'biz_name': '-',
                            'bot_id': 'oCErvJo4hA3EAJYN',
                            'bot_name': 'BK-ChatBot',
                            'bot_type': 'default',
                            'created_by': 'system',
                            'created_at': '2021-04-23 15:58:48',
                            'updated_at': '1970-01-01 00:00:00'
                        }
                    ]
                },
                'request_id': '8cae7459-42e0-4c8c-b375-470d16258e69'
            }
        },
        getBiz (context, params, config = {}) {
            const mockUrl = `${AJAX_URL_PREFIX}/api/v1/biz/describe_biz/?${AJAX_MOCK_PARAM}=cc&invoke=cc`
            return http.post(mockUrl, params, config)
        }
    }
}

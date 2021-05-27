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
 */

import http from '@/api'

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

        getLogTableData (context, params, config = {}) {
            const mockUrl = `${AJAX_URL_PREFIX}/api/v1/log/describe_logs/?${AJAX_MOCK_PARAM}=intent&invoke=logList`
            return http.post(mockUrl, params, config)
        },
        getRecordTableData (context, params, config = {}) {
            const mockUrl = `${AJAX_URL_PREFIX}/api/v1/log/describe_records/?${AJAX_MOCK_PARAM}=intent&invoke=recordList`
            return http.post(mockUrl, params, config)
        },
        getBotNum (context, params, config = {}) {
            const mockUrl = `${AJAX_URL_PREFIX}/api/v1/` + params.bizId + `/bot/fetch_bot_count/?${AJAX_MOCK_PARAM}=intent&invoke=botNum`
            return http.post(mockUrl, params, config)
        },
        getIntentNum (context, params, config = {}) {
            const mockUrl = `${AJAX_URL_PREFIX}/api/v1/` + params.bizId + `/intent/fetch_intent_count/?${AJAX_MOCK_PARAM}=intent&invoke=intentNum`
            return http.post(mockUrl, params, config)
        }
    }
}

/**
 *TencentBlueKing is pleased to support the open source community by making
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
 * @file auth
 * @author
 */

import store from '@/store'

const ANONYMOUS_USER = {
    id: null,
    isAuthenticated: false,
    username: 'anonymous'
}

let currentUser = {
    id: '',
    username: ''
}

export default {
    /**
     * 未登录状态码
     */
    HTTP_STATUS_UNAUTHORIZED: 401,

    /**
     * 获取当前用户
     *
     * @return {Object} 当前用户信息
     */
    getCurrentUser () {
        return currentUser
    },

    redirectToLogin () {
        window.location = '/?c_url=' + encodeURIComponent(window.location.href)
    },

    /**
     * 请求当前用户信息
     *
     * @return {Promise} promise 对象
     */
    requestCurrentUser () {
        let promise = null
        if (currentUser.isAuthenticated) {
            promise = new Promise((resolve, reject) => {
                resolve(currentUser)
            })
        } else {
            if (!store.state.user || !Object.keys(store.state.user).length) {
                // store action userInfo 里，如果请求成功会更新 state.user
                const req = store.dispatch('userInfo')
                promise = new Promise((resolve, reject) => {
                    req.then(resp => {
                        // 存储当前用户信息(全局)
                        currentUser = store.getters.user
                        currentUser.isAuthenticated = true
                        resolve(currentUser)
                    }, err => {
                        if (err.response.status === this.HTTP_STATUS_UNAUTHORIZED || err.crossDomain) {
                            resolve({ ...ANONYMOUS_USER })
                        } else {
                            reject(err)
                        }
                    })
                })
            }
        }

        return promise
    }
}

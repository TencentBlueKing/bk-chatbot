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

import Vue from 'vue'
import VueRouter from 'vue-router'

import store from '@/store'
import http from '@/api'
import preload from '@/common/preload'

const MainEntry = () => import(/* webpackChunkName: 'entry' */'@/views')
const NotFound = () => import(/* webpackChunkName: 'none' */'@/views/404')
const BotList = () => import(/* webpackChunkName: 'entry' */'@/views/bot')
const IntentList = () => import(/* webpackChunkName: 'entry' */'@/views/intent/list')
const KnowledgeBase = () => import(/* webpackChunkName: 'entry' */'@/views/admin/knowledge')
const Chart = () => import(/* webpackChunkName: 'entry' */'@/views/chart')
const Group = () => import(/* webpackChunkName: 'entry' */'@/views/group')

Vue.use(VueRouter)

const routes = [
    {
        path: window.PROJECT_CONFIG.SITE_URL,
        name: 'appMain',
        component: MainEntry,
        alias: '',
        children: [
            {
                path: 'index',
                alias: '',
                name: 'index',
                component: Chart,
                meta: {
                    matchRoute: '首页'
                }
            },
            {
                path: 'bot/list',
                name: 'bot-list',
                component: BotList,
                meta: {
                    matchRoute: '机器人'
                }
            },
            {
                path: 'intent/list',
                name: 'intent-list',
                component: IntentList,
                meta: {
                    matchRoute: '技能中心'
                }
            },
            {
                path: 'group/bind',
                name: 'group-bind',
                component: Group,
                meta: {
                    matchRoute: '业务群'
                }
            },
            {
                path: 'admin/knowledge-base',
                name: 'admin-knowledge-base',
                component: KnowledgeBase,
                meta: {
                    matchRoute: '知识库'
                }
            }
        ]
    },
    // 404
    {
        path: '*',
        name: '404',
        component: NotFound
    }
]

const router = new VueRouter({
    mode: 'history',
    routes: routes
})

const cancelRequest = async () => {
    const allRequest = http.queue.get()
    const requestQueue = allRequest.filter(request => request.cancelWhenRouteChange)
    await http.cancel(requestQueue.map(request => request.requestId))
}

let preloading = true
let canceling = true
let pageMethodExecuting = true

router.beforeEach(async (to, from, next) => {
    canceling = true
    await cancelRequest()
    canceling = false
    next()
})

router.afterEach(async (to, from) => {
    store.commit('setMainContentLoading', true)

    preloading = true
    await preload()
    preloading = false

    const pageDataMethods = []
    const routerList = to.matched
    routerList.forEach(r => {
        Object.values(r.instances).forEach(vm => {
            if (typeof vm.fetchPageData === 'function') {
                pageDataMethods.push(vm.fetchPageData())
            }
            if (vm.$options.preload === 'function') {
                pageDataMethods.push(vm.$options.preload.call(vm))
            }
        })
    })

    pageMethodExecuting = true
    await Promise.all(pageDataMethods)
    pageMethodExecuting = false

    if (!preloading && !canceling && !pageMethodExecuting) {
        store.commit('setMainContentLoading', false)
    }
})

export default router
